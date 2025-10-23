import os
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from config import Config

class ScholarshipSummarizer:
    def __init__(self):
        self.openai_api_key = Config.OPENAI_API_KEY
        self.use_openai = bool(self.openai_api_key) and OPENAI_AVAILABLE
        self.use_transformers = TRANSFORMERS_AVAILABLE

        if self.use_openai:
            openai.api_key = self.openai_api_key
        elif self.use_transformers:
            # Use local model as fallback
            self.setup_local_model()
        else:
            print("⚠️  No AI summarization available - install openai or transformers package")

    def setup_local_model(self):
        """Setup local summarization model"""
        if not self.use_transformers:
            return

        try:
            model_name = "facebook/bart-large-cnn"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

            # Use GPU if available
            self.device = 0 if torch.cuda.is_available() else -1
            self.summarizer = pipeline(
                "summarization",
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device
            )
            print("✅ Local summarization model loaded")
        except Exception as e:
            print(f"⚠️  Could not load local model: {e}")
            self.summarizer = None

    def summarize_with_openai(self, text, max_length=150):
        """Summarize text using OpenAI"""
        if not OPENAI_AVAILABLE:
            return self.fallback_summary(text)

        try:
            prompt = f"Please summarize the following scholarship opportunity in {max_length} words or less, focusing on key benefits, eligibility requirements, and application process:\n\n{text}"

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=min(max_length * 2, 300),  # Allow some buffer
                temperature=0.3
            )

            summary = response.choices[0].message.content.strip()
            return summary

        except Exception as e:
            print(f"Error with OpenAI summarization: {e}")
            return self.fallback_summary(text)

    def summarize_with_local_model(self, text, max_length=150):
        """Summarize text using local transformer model"""
        if not self.use_transformers or not self.summarizer:
            return self.fallback_summary(text)

        try:
            # Truncate text if too long
            max_input_length = 1024
            if len(text) > max_input_length:
                text = text[:max_input_length]

            summary = self.summarizer(
                text,
                max_length=min(max_length, 150),
                min_length=50,
                do_sample=False
            )

            return summary[0]['summary_text']

        except Exception as e:
            print(f"Error with local summarization: {e}")
            return self.fallback_summary(text)

    def fallback_summary(self, text):
        """Simple fallback summarization"""
        sentences = text.split('.')
        if len(sentences) <= 3:
            return text

        # Take first and last few sentences
        first_part = '.'.join(sentences[:2])
        last_part = '.'.join(sentences[-2:]) if len(sentences) > 3 else ''

        summary = first_part
        if last_part and not last_part.startswith(first_part[:50]):
            summary += '. ' + last_part

        return summary[:300] + ('...' if len(summary) > 300 else '')

    def summarize_scholarship(self, text, max_length=150):
        """Main summarization function"""
        if not text or len(text.strip()) < 50:
            return text

        if self.use_openai:
            return self.summarize_with_openai(text, max_length)
        elif self.use_transformers:
            return self.summarize_with_local_model(text, max_length)
        else:
            return self.fallback_summary(text)

    def batch_summarize(self, scholarships):
        """Summarize multiple scholarships"""
        for scholarship in scholarships:
            if scholarship.get('description') and not scholarship.get('summary'):
                summary = self.summarize_scholarship(scholarship['description'])
                scholarship['summary'] = summary

        return scholarships
