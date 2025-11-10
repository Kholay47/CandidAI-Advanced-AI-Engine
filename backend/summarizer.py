import os
from pathlib import Path
import logging

LOCAL_HF_MODEL = Path("models/optional_hf_llms/bart-large-cnn")
use_local_hf = LOCAL_HF_MODEL.exists()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


if use_local_hf:
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

    def _load_model_and_tokenizer(model_path: str):
        """Load tokenizer/model safely, auto-fix vocab mismatch, and persist resized model."""
        resized_path = Path(model_path + "-resized")

        # ✅ Prefer the resized folder if it already exists
        if resized_path.exists():
            logger.info(f"Loading resized model from {resized_path}")
            tokenizer = AutoTokenizer.from_pretrained(resized_path, use_fast=True)
            model = AutoModelForSeq2SeqLM.from_pretrained(resized_path)
        else:
            tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

            vocab_tok = getattr(tokenizer, "vocab_size", len(tokenizer))
            vocab_model = getattr(model.config, "vocab_size", None)
            max_pos = getattr(model.config, "max_position_embeddings", None)
            logger.info(
                f"Tokenizer.vocab_size={vocab_tok}, Model.vocab_size={vocab_model}, Model.max_position_embeddings={max_pos}"
            )

            # ⚙️ Fix vocab mismatch once and save resized copy
            if vocab_model is not None and vocab_tok > vocab_model:
                logger.warning(
                    "Tokenizer vocabulary larger than model embeddings. Resizing model token embeddings."
                )
                model.resize_token_embeddings(vocab_tok)
                save_dir = resized_path
                save_dir.mkdir(parents=True, exist_ok=True)
                try:
                    tokenizer.save_pretrained(save_dir)
                    model.save_pretrained(save_dir)
                    logger.info(f"Resized model and tokenizer saved to {save_dir}")
                except Exception as e:
                    logger.warning(f"Could not save resized model: {e}")

        # ✅ Ensure pad token exists
        if tokenizer.pad_token is None:
            if tokenizer.eos_token is not None:
                tokenizer.pad_token = tokenizer.eos_token
            else:
                tokenizer.add_special_tokens({"pad_token": "<pad>"})
            model.config.pad_token_id = tokenizer.pad_token_id

        # ✅ Add forced_bos_token_id if missing (for BART)
        if getattr(model.config, "forced_bos_token_id", None) is None:
            model.config.forced_bos_token_id = tokenizer.bos_token_id or 0

        device = 0 if torch.cuda.is_available() else -1
        summarizer_pipe = pipeline(
            "summarization", model=model, tokenizer=tokenizer, device=device
        )
        return summarizer_pipe, tokenizer, model

    # --- Load model ---
    try:
        summarizer, tokenizer, hf_model = _load_model_and_tokenizer(str(LOCAL_HF_MODEL))
    except Exception as e:
        logger.exception("Initial load failed, trying resized model path fallback.")
        summarizer, tokenizer, hf_model = _load_model_and_tokenizer(
            str(LOCAL_HF_MODEL) + "-resized"
        )

else:
    # Fallback to OpenAI
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    logger.info("Local summarizer not found. Using OpenAI fallback.")


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def _token_chunker_by_tokens(text: str, tokenizer, max_tokens: int, stride: int = 32):
    """Yield slices of text such that each slice token length <= max_tokens."""
    input_ids = tokenizer.encode(text, add_special_tokens=False)
    total = len(input_ids)
    if total <= max_tokens:
        yield text
        return

    start = 0
    while start < total:
        end = min(start + max_tokens, total)
        chunk_ids = input_ids[start:end]
        chunk_text = tokenizer.decode(
            chunk_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )
        yield chunk_text
        if end == total:
            break
        start += max_tokens - stride


def _summarize_chunks_and_combine(
    chunks, summarizer_pipe, tokenizer, max_summary_tokens=150
):
    chunk_summaries = []
    for ch in chunks:
        try:
            out = summarizer_pipe(
                ch,
                truncation=True,
                max_length=max_summary_tokens,
                min_length=max(20, max_summary_tokens // 3),
                do_sample=False,
            )
            text = (
                out[0].get("summary_text", "").strip()
                if isinstance(out, list)
                else out.get("summary_text", "").strip()
            )
            chunk_summaries.append(text)
        except Exception as e:
            logger.exception("Chunk summarization failed; returning partial text.")
            chunk_summaries.append(ch[:1000])

    combined = " ".join(chunk_summaries).strip()
    if not combined:
        return ""

    # If still long, summarize once more
    if (
        len(tokenizer.encode(combined, add_special_tokens=False))
        > max_summary_tokens * 3
    ):
        try:
            final = summarizer_pipe(
                combined,
                truncation=True,
                max_length=max_summary_tokens + 20,
                min_length=30,
                do_sample=False,
            )
            return final[0]["summary_text"].strip()
        except Exception:
            logger.exception(
                "Final summarization pass failed; returning combined chunk summaries."
            )
            return combined[:2000]
    return combined


# ---------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------
def generate_summary(text: str, max_words: int = 60) -> str:
    """Generate concise summary of resume text using local HF or OpenAI fallback."""
    if use_local_hf:
        approx_tokens_for_output = max(30, max_words * 2)

        try:
            model_max_pos = getattr(hf_model.config, "max_position_embeddings", None)
            tokenizer_max_len = getattr(tokenizer, "model_max_length", None)
            if not tokenizer_max_len or tokenizer_max_len <= 0:
                tokenizer_max_len = 1024
            effective_max_input = min(
                [x for x in [model_max_pos, tokenizer_max_len] if x is not None],
                default=1024,
            )
            chunk_token_size = effective_max_input - 50

            tokids = tokenizer.encode(text, add_special_tokens=False)
            if len(tokids) <= chunk_token_size:
                out = summarizer(
                    text,
                    truncation=True,
                    max_length=approx_tokens_for_output,
                    min_length=max(20, approx_tokens_for_output // 3),
                    do_sample=False,
                )
                return out[0]["summary_text"].strip()

            # For long text
            chunks = list(
                _token_chunker_by_tokens(
                    text, tokenizer, max_tokens=chunk_token_size, stride=50
                )
            )
            return _summarize_chunks_and_combine(
                chunks,
                summarizer,
                tokenizer,
                max_summary_tokens=approx_tokens_for_output,
            )

        except Exception as e:
            logger.exception("Error during local HF summarization")
            return f"Error generating summary with local HF model: {str(e)}"

    else:
        # --- OpenAI fallback ---
        prompt = f"""
        Summarize the following resume text into {max_words} words or less.
        Focus on skills, experience, and education.
        Make it concise and recruiter-friendly:

        Resume:
        {text}
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating summary via OpenAI: {str(e)}"
