# Portfolio

All three projects are public, and none of them uses an employer's work.

## Honest Mistake: evaluating an LLM agent that audits models for data leakage

https://github.com/sidharthjatt/honest-mistake

I built this on my own. It is the closest thing I have to the work in this role. The agent is not a coding agent, but building it meant solving the same problems: a trustworthy answer key, a fair scorer, planted test cases, and honest reporting.

What I did:
- Wrote the answer key (which columns leak) before building the agent, and kept the word "leakage" out of its prompt so it could not be steered to the answer.
- Built the scorer that compares the agent's findings with the answer key.
- Planted a leaking column on purpose as a canary. The agent caught it in all three canary setups.
- Kept a run register with every run, including one I marked unusable because it hit the turn limit.
- Kept mock runs and real runs apart, and refused to score runs that were cut off.
- Tested my own evaluation: I found and wrote up a blind spot in my scorer, and an ablation that could not answer its own question.

## Reasonable Doubt: legal clause classifier, fine-tuned encoder against LLMs

https://github.com/sidharthjatt/reasonable-doubt

I built this on my own. I fixed the comparison rules before each run, and the CI is set up to run without any API key.

## Predictive Engine: ranking system for Indian equities

https://github.com/sidharthjatt/predictive-engine

I built this during my M.Tech under the guidance of my supervisor, Dr. Sandeep Yadav, and an industry practitioner with about 15 years of experience in the field. Every experiment was judged against acceptance rules I wrote down before running it.
