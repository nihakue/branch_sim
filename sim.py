import numpy as np

def sim(pred, file='gcc_branch.out'):
    trace = {}
    fail_rate = 0
    with open(file, 'r') as f:
        for line in f:
            reg = line[2:8]
            result = int(line[9])
            trace.setdefault(reg, []).append(int(line[9]))

    corrects = sum(pred(s) for s in trace.values())
    total = sum(len(r) for r in trace.values())
    return corrects * 1.0/total

def static_pred_take(branch):
    return sum(s & 1 for s in branch)


