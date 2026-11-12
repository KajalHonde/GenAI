# How LLMs Work

## 1. What is an LLM?

LLM means Large Language Model. It is an AI model trained on a very large amount of text. It learns patterns in language so it can understand a prompt and generate a useful response.

Examples include ChatGPT, Gemini and Claude.

## 2. How does an LLM work?

1. **User input:** A person types a question or instruction.
2. **Tokenization:** The text is split into small pieces called tokens.
3. **Embeddings:** Tokens are changed into numerical representations that the model can process.
4. **Transformer:** The transformer uses attention to understand how words and tokens relate to one another.
5. **Prediction:** The model predicts a likely next token based on the input and the tokens already generated.
6. **Response:** It repeats this process to generate a response, then the text is shown to the user.

## 3. Diagram

```text
 User question
      |
      v
 Tokenization
      |
      v
 Token embeddings
      |
      v
 Transformer + attention
      |
      v
 Predict next token
      |
      v
 Generate tokens one by one
      |
      v
 Final answer
```

## 4. Where are LLMs used?

- Question-answering chatbots
- Summarizing long text
- Translation
- Writing assistance
- Coding assistance

## 5. LLMs in AapdaMitra

AapdaMitra can use an LLM to understand disaster-related questions and explain safety information in simple language. For example, a user may ask what to do during a flood or earthquake.

The answer should be based on trusted disaster-safety information. An LLM does not automatically know live local conditions. If the available data does not contain an answer, the application should say that it cannot verify the information instead of guessing.

**Important:** This document explains the general working of an LLM. It does not claim that this starter FastAPI application already contains or runs an LLM.
