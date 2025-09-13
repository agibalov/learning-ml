# langchain-experiment

Learning [LangChain](https://www.langchain.com/).

## How to do things

* `uv run pytest` to run all tests
* `uv run pytest -k 'test_agent_sql and model_ollama_llama3_2_3b and temp_0_2 and seed_1337'` to run all agent tests from `test_agent_sql.py` using the specified parameters.
* `uv run pytest -k 'test_count_persons_older_than_30 and model_ollama_llama3_2_3b and temp_0_2 and seed_1337'` to run `test_count_persons_older_than_30` from `test_agent_sql.py` using the specified parameters.

## test_agent_sql.py

`tests/test_agent_sql.py` is an effort to build an agent that makes SQL queries against an in-memory sqlite database to answer user's questions. When using `llama3.2:3b`, it occasionally has difficulties answering what the name of the oldest person is:

|        filepath         |             function             |                    params                    | passed | failed | SUBTOTAL |
| ----------------------- | -------------------------------- | -------------------------------------------- | -----: | -----: | -------: |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_0-seed_0       |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_0-seed_1337    |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_0-seed_2302    |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_0-seed_31337   |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_0_2-seed_0     |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_0_2-seed_1337  |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_0_2-seed_2302  |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_0_2-seed_31337 |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_0_6-seed_0     |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_0_6-seed_1337  |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_0_6-seed_2302  |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_0_6-seed_31337 |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_1-seed_0       |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_1-seed_1337    |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_1-seed_2302    |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_llama3_2_3b-temp_1-seed_31337   |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_0-seed_0       |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_0-seed_1337    |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_0-seed_2302    |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_0-seed_31337   |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_0_2-seed_0     |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_0_2-seed_1337  |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_0_2-seed_2302  |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_0_2-seed_31337 |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_0_6-seed_0     |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_0_6-seed_1337  |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_0_6-seed_2302  |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_0_6-seed_31337 |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_1-seed_0       |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_1-seed_1337    |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_1-seed_2302    |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_llama3_2_3b-temp_1-seed_31337   |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_0-seed_0       |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_0-seed_1337    |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_0-seed_2302    |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_0-seed_31337   |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_0_2-seed_0     |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_0_2-seed_1337  |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_0_2-seed_2302  |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_0_2-seed_31337 |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_0_6-seed_1337  |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_0_6-seed_2302  |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_0_6-seed_31337 |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_1-seed_1337    |      1 |      0 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_0_6-seed_0     |      0 |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_1-seed_0       |      0 |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_1-seed_2302    |      0 |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_llama3_2_3b-temp_1-seed_31337   |      0 |      1 |        1 |
| TOTAL                   |                                  |                                              |     44 |      4 |       48 |

*To generate this table `run uv run pytest -k 'test_agent_sql and model_ollama_llama3_2_3b' --md-report --md-report-verbose=2`*

With `gpt-oss:20b` it always (?) works:

|        filepath         |             function             |                    params                    | passed | SUBTOTAL |
| ----------------------- | -------------------------------- | -------------------------------------------- | -----: | -------: |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_0-seed_0       |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_0-seed_1337    |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_0-seed_2302    |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_0-seed_31337   |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_0_2-seed_0     |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_0_2-seed_1337  |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_0_2-seed_2302  |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_0_2-seed_31337 |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_0_6-seed_0     |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_0_6-seed_1337  |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_0_6-seed_2302  |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_0_6-seed_31337 |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_1-seed_0       |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_1-seed_1337    |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_1-seed_2302    |      1 |        1 |
| tests/test_agent_sql.py | test_count_persons_older_than_30 | model_ollama_gpt_oss_20b-temp_1-seed_31337   |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_0-seed_0       |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_0-seed_1337    |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_0-seed_2302    |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_0-seed_31337   |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_0_2-seed_0     |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_0_2-seed_1337  |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_0_2-seed_2302  |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_0_2-seed_31337 |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_0_6-seed_0     |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_0_6-seed_1337  |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_0_6-seed_2302  |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_0_6-seed_31337 |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_1-seed_0       |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_1-seed_1337    |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_1-seed_2302    |      1 |        1 |
| tests/test_agent_sql.py | test_average_age                 | model_ollama_gpt_oss_20b-temp_1-seed_31337   |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_0-seed_0       |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_0-seed_1337    |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_0-seed_2302    |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_0-seed_31337   |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_0_2-seed_0     |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_0_2-seed_1337  |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_0_2-seed_2302  |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_0_2-seed_31337 |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_0_6-seed_0     |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_0_6-seed_1337  |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_0_6-seed_2302  |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_0_6-seed_31337 |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_1-seed_0       |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_1-seed_1337    |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_1-seed_2302    |      1 |        1 |
| tests/test_agent_sql.py | test_name_of_oldest_person       | model_ollama_gpt_oss_20b-temp_1-seed_31337   |      1 |        1 |
| TOTAL                   |                                  |                                              |     48 |       48 |

*To generate this table run `uv run pytest -k 'test_agent_sql and model_ollama_gpt_oss_20b' --md-report --md-report-verbose=2`*