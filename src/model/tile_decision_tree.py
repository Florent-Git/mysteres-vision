import pickle


def get_decision_tree():
    '''
    Loads the model from the model directory
    '''
    with open('model/mysteres01.pkl', 'rb') as f:
        model = pickle.load(f)
    return model