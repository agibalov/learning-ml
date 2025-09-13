from pydantic_core import ValidationError
from expert import check_text_entail_claim

TEST_REPETITIONS = 100

def test_check_text_entail_claim_works():
    correct_count = 0
    incorrect_count = 0
    crash_count = 0
    for _ in range(TEST_REPETITIONS):
        try:
            result = check_text_entail_claim("The sky is blue.", "Blue is the sky's color.")
            if result.is_true:
                correct_count += 1
            else:
                print(f"Incorrect result: {result}")
                incorrect_count += 1            
        except ValidationError as e:
            print(f"ValidationError: {e}")
            crash_count += 1
    assert correct_count == TEST_REPETITIONS
    assert incorrect_count == 0    
    assert crash_count == 0
