from safetycourse.bayes import BinaryNode, BinaryBayesNet


def test_diagnostic_inference():
    net = BinaryBayesNet([
        BinaryNode("Fault", [], {(): 0.1}),
        BinaryNode("Alarm", ["Fault"], {(False,): 0.05, (True,): 0.9}),
    ])
    assert net.query("Fault", {"Alarm": True})[True] > 0.1
