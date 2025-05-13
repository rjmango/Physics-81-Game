from states.state import State

class StateName(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.load_assets()
        # Other parts sa code | add variables

    def update(self):
        # Code for updating values
        pass

    def render(self, display):
        # render background in screen
        display.blit(self.bg, (0,0))
        # Code for displaying screens
        pass

    def load_assets(self):
        # Load background by changing parameter
        self.bg = self.game.load_background_asset("assets/bg/main-menu-bg1.png")
        # Example
        # self.bg = self.game.load_background_asset("assets/bg/new-bg.png")

        # load other assets
        # self.asset_name = pygame.image.load("Enter filepath here").convert_alpha()
