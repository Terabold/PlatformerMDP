class StateControl:
    def __init__(self, initial_state='menu'):
        self.currentState = initial_state
        self.previousStates = [initial_state]

    def getState(self):
        return self.currentState
    
    def setState(self, state):
        self.currentState = state
        self.previousStates.append(self.currentState)
    
    def returnToPrevState(self):
        if len(self.previousStates) >= 2:
            self.previousStates.pop()
            self.currentState = self.previousStates[-1]
        else:
            self.currentState = 'menu'

state_control = StateControl('menu')