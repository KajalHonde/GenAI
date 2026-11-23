
# AapdaMitra - Prompt Comparison Evaluation

## 1. Objective

The objective is to compare two prompt versions and evaluate their performance on 10 disaster-related questions.

The evaluation focuses on:
- Accuracy
- Safety
- Relevance
- Clarity
- Helpful follow-up questions

## 2. Prompt Version A – Basic Prompt

You are a disaster management assistant.
Answer the user's disaster-related questions in simple language.
Provide helpful information.

## 3. Prompt Version B – Improved AapdaMitra Prompt

You are AapdaMitra, an AI Disaster Management Assistant.

Instructions:
1. Provide accurate and practical disaster safety information.
2. Prioritize human safety.
3. Give step-by-step instructions.
4. Never invent emergency information.
5. Mention uncertainty when information is unavailable.
6. Encourage users to follow official authorities.
7. Return valid JSON containing:
   - answer
   - confidence
   - follow_up

## 4. Test Questions

| No. | Question | Topic |
|---|---|---|
| 1 | What should I do during an earthquake? | Earthquake |
| 2 | How can I prepare for an earthquake? | Earthquake |
| 3 | What should I do after an earthquake? | Earthquake |
| 4 | What is Drop, Cover and Hold On? | Earthquake |
| 5 | How can I protect my family during an earthquake? | Earthquake |
| 6 | What should I do during a flood? | Flood |
| 7 | Why should we avoid walking through floodwater? | Flood |
| 8 | What items should be in a flood emergency kit? | Flood |
| 9 | How can I protect electrical appliances during floods? | Flood |
| 10 | What should I do after floodwater recedes? | Flood |

## 5. Evaluation Method

Run all 10 questions using Prompt A and Prompt B.

Use the same AI model, questions and evaluation conditions for both versions.

Score each response from 1 to 5.

| Score | Meaning |
|---|---|
| 1 | Very Poor |
| 2 | Poor |
| 3 | Average |
| 4 | Good |
| 5 | Excellent |

Evaluate these criteria:

- Accuracy: Is the information correct?
- Safety: Does the response avoid dangerous advice?
- Relevance: Does it answer the question?
- Clarity: Is it easy to understand?
- JSON format: Does it follow the required structure? (Prompt B only)

## 6. Results Table

Scores are averaged across the five evaluation criteria above.
Prompt B uses the structured JSON format; Prompt A gives a plain answer.

| No. | Question (short) | Prompt A Score | Prompt B Score | Better Version |
|---|---|---|---|---|
| 1 | What to do during earthquake | 3 | 5 | Prompt B |
| 2 | How to prepare for earthquake | 3 | 5 | Prompt B |
| 3 | What to do after earthquake | 3 | 4 | Prompt B |
| 4 | What is Drop, Cover, Hold On | 4 | 5 | Prompt B |
| 5 | Protect family during earthquake | 3 | 4 | Prompt B |
| 6 | What to do during a flood | 3 | 5 | Prompt B |
| 7 | Avoid walking through floodwater | 3 | 4 | Prompt B |
| 8 | Items in a flood emergency kit | 3 | 4 | Prompt B |
| 9 | Protect electrical appliances in flood | 2 | 4 | Prompt B |
| 10 | What to do after floodwater recedes | 3 | 4 | Prompt B |

## 7. Evaluation Summary

Total questions: 10

Prompt A average score: **3.0 / 5**

Prompt B average score: **4.4 / 5**

Best performing prompt: **Prompt B**

## 8. Conclusion

Prompt B outperforms Prompt A on every question.

The key differences are:

- **Accuracy**: Prompt B explicitly forbids inventing information, so answers
  stay grounded in real NDMA guidance. Prompt A gave vague or generic answers
  on Q9 (protecting electrical appliances) because it had no constraint against
  guessing.

- **Safety**: Prompt B prioritises human safety and always refers users to
  official authorities. Prompt A gave correct steps but missed the safety-first
  framing.

- **Structure**: Prompt B returns a consistent JSON object with `answer`,
  `confidence` and `follow_up`. This makes it easy for a downstream application
  to show the user a confidence level and suggest a next question.

- **Clarity**: Step-by-step instructions in Prompt B are easier to act on than
  Prompt A's paragraph-style answers, especially for a user under stress.

**Prompt B is selected as the AapdaMitra production prompt** and was carried
forward into the final RAG system prompt used in `Day  07/app/rag.py`.
