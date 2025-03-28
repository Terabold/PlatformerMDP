
class state:

    def __init__(self, currentState) -> None:
        self.currentState = currentState
        self.previousStates = [currentState]

    def getState(self):
        return self.currentState
    
    # def returnToPrevState(self):
    #     if len(self.previousStates) >= 2:
    #         self.previousStates.pop()
    #         self.currentState = self.previousStates[-1]
    #     else: self.currentState = 'menu'
    
    def setState(self, state):
        self.currentState = state
        self.previousStates.append(self.currentState)

state_control = state('menu')