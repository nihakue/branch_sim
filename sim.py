import pdb

def sim(pred, file='gcc_branch.out', **kwargs):
    '''Simulate a branch predictor [pred] on trace output contained in [file].

    :param: pred should be a function that takes a single parameter 'branch',
    which is a list of [0/1] values indicating branch outcome,pred should return
    the total number of correct predictions for that branch.

    :param: file should be a string containing the file path for a trace output

    :returns: the misprediction rate of the predictor in the form of:
    1 - (correct predictions / total branches)
    '''
    #Create a dictionary that will be keyed by branch addresses
    trace = {}
    with open(file, 'r') as file_in:
        for line in file_in:
            #Seperate the address from the result
            register = line[2:8]
            result = int(line[9])
            #append the branch result to the list of results for this branch
            trace.setdefault(register, []).append(result)

    #Use predictor to get total number of correct predictions
    if 'n' in kwargs:
        #Special case for adaptive predictors
        num_correct = sum(pred(s, n=kwargs['n']) for s in trace.values())
    else:
        num_correct = sum(pred(s) for s in trace.values())
    #Get the length of all result lists for all branches
    total = sum(len(r) for r in trace.values())
    return 1 - (num_correct * 1.0/total)

def static_pred_take(branch):
    '''Always predict take'''
    return sum((r & 1) for r in branch)


def static_pred_notake(branch):
    '''Always predict not taken'''
    return sum(((not r & 1) for r in branch))

def profile_pred(branch):
    '''Profile a branch first, and only predict take if >50 percent takes'''
    takes = sum(branch)
    if takes * 1.0 / len(branch) >= .5:
        return static_pred_take(branch)
    else:
        return static_pred_notake(branch)

def two_bit_no_history_pred(branch):
    '''using a simple 2-bit saturating history'''
    state = 1
    num_correct = 0

    for outcome in branch:
        #Based on slide 10, lecture 05:
        prediction = (state > 1)
        if prediction == outcome:
            num_correct += 1

        state = state + 1 if outcome else state - 1
        state = 3 if state > 3 else state
        state = 0 if state < 0 else state

    return num_correct

def two_level_ad_pred(branch, n=1):
    num_correct = 0
    #Pattern history table is a dictionary indexed by history
    p_history = {}
    for i in range(0, len(branch)):
        #We pad new branches with 0s in their pattern history tables
        if i < n:
            padding = [0 for s in range(n - i)]
            history = padding + branch[:i]
        else:
            #Otherwise we just get the last n outcomes
            history = branch[i-n:i]

        #Cast to string to use as key
        history = str(history)
        #If this is a new 2-bit counter, start it at state 01
        state = (p_history.setdefault(history, 1))
        #Because we're using 2 bits, prediction is simply:
        prediction = (state > 1)
        outcome = branch[i]
        if prediction == outcome:
            num_correct += 1

        #Advance state machine, making sure to avoid over/underflow
        state = p_history[history]
        state = state + 1 if outcome else state - 1
        state = 3 if state > 3 else state
        state = 0 if state < 0 else state
        p_history[history] = state

    return num_correct


def main():
    print "If the gcc and mcf stack traces are in your current directory, skip"
    gcc = raw_input('relative/absolute filepath for the gcc stack trace:\n')
    mcf = raw_input('relative/absolute filepath for the mcf stack trace:\n')
    if gcc == '':
        gcc = 'gcc_branch.out'
    if mcf == '':
        mcf = 'mcf_branch.out'
    print "Predictor\tgcc miss %\tmcf miss %"
    print "Static (Take)\t %.6f\t%.6f" % (sim(static_pred_take, file=gcc),
                                                    sim(static_pred_take, file=mcf))

if __name__ == '__main__':
    main()
