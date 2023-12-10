import json

from user_status_estimator import UserStatusEstimator

estimator = UserStatusEstimator()

with open("test_input.json") as fp:
    test_input = json.load(fp)

for payload in test_input:
    result = estimator.estimate(payload)
    print(str(result))


