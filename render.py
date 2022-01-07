import pygame
from time import sleep
import copy
import chess
from sys import exit

scale = 80

class SpriteSheet:

    def __init__(self, filename):
        """Load the sheet."""
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

        self.x_padding=68
        self.y_padding=144


    def image_at(self, rectangle, colorkey = None):
        """Load a specific image from a specific rectangle."""
        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect(rectangle)
        original_image = pygame.Surface(rect.size, pygame.SRCALPHA)
        image = original_image.copy()
        # this works on images with per pixel alpha too
        alpha = 0
        image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        image.blit(self.sheet, (10, 10), rect)
        image = pygame.transform.scale(image, (95, 95))
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey = None):
        """Load a whole bunch of images and return them as a list."""
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey = None):
        """Load a whole strip of images, and return them as a list."""
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

    def load_all(self):
        rect_start = [64, 73, 100, 100]
        rects = []
        for i in range(6):
            rects.append([rect_start[0] + self.x_padding*i + rect_start[2] * i, rect_start[1], rect_start[2], rect_start[3]])
        rect_start = [64, 73+self.y_padding, 100, 100]
        for i in range(6):
            rects.append([rect_start[0] + self.x_padding*i + rect_start[2] * i, rect_start[1], rect_start[2], rect_start[3]])
        self.pieces = self.images_at(rects)

class Piece(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the block,
    # and its x and y position'
    def __init__(self, screen, x, y, type, color, sheet):
       # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        if type == "King":
                col = 0
        elif type == "Queen":
                col = 1
        elif type == "Rook":
                col = 2
        elif type == "Bishop":
                col = 3
        elif type == "Knight":
                col = 4
        elif type == "Pawn":
                col = 5
        
        if color == "B":
            row = 0
        else:
            row = 1
        image = sheet.pieces[row*6 +col]
        self.image = image
        

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def blitme(self):
        """Draw the piece at its current location."""
        self.screen.blit(self.image, self.rect)

    def blitme_small(self):
        self.image = pygame.transform.scale(self.image, (60, 60))
        """Draw the piece at its current location."""
        self.screen.blit(self.image, self.rect)

class GameRendering:
    def __init__(self, game):
        pygame.init()
        pygame.font.init()
        
        self.side_length = 80
        self.game = game
        self.done = False
        self.height = 8
        self.width = 8
        self.imagerect = (0, 0)
        self.black = (120,120,120)
        self.white = (255, 255, 255)
        self.green = (0, 255, 0)
        self.open = (125, 125, 125)
        self.blue = (0,0,125)
        self.screen = pygame.display.set_mode([self.width*scale + 200, scale* self.height])
        self.text = pygame.font.SysFont('Comic Sans MS', 30)
        self.sheet = SpriteSheet("sprites/chess_pieces.png")
        self.sheet.load_all()
        self.mark = 1
        moves = []
        selected = 0
        while True:
            self.mouse_pos = pygame.mouse.get_pos()
            self.render(moves, selected)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if self.game.promotee: 
                        if  pos[0] > 700 and pos[0] < 760:
                            print(self.game.promotee)
                            officers = [150, 250, 350,450]
                            for officer in officers:
                                if pos[1] > officer and pos[1] < officer + 60:
                                    pick = officer
                                    break
                            if pick == 150:
                                pick = "Queen"
                            elif pick == 250:
                                pick = "Rook"
                            elif pick == 350:
                                pick = "Knight"
                            elif pick == 450:
                                pick = "Bishop"
                            if pick: 
                                self.game.promote(pick)

                    elif selected:
                        if [pos[0] // scale, pos[1] // scale] in moves:
                            positions = [[piece.position[0], piece.position[1]],[pos[0] // scale, pos[1] // scale]]
                            game.move(positions, piece.color)
                            moves = []
                            selected = 0
                        else:
                            moves = []
                            selected = 0
                    else:
                        print("else")
                        piece = game.board[pos[0] // scale][ pos[1] // scale]
                        if piece != 0:
                            if piece.color == game.next_to_move:
                                selected = piece
                                moves = piece.get_possible_moves()
                            else:
                                selected = 0
                                moves = []
                        else:
                            selected = 0
                            moves = []
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

    def render(self, moves, selected):
        self.screen.fill(self.white)
        mark = self.mark
        if not self.done:
            textsurface = self.text.render("Spiller: " + str(mark), True, (0, 0, 0))
            self.screen.blit(textsurface,(400,0))
        else:
            textsurface = self.text.render("Spiller:" + str(mark) + " Vant", True, (0, 0, 0))
            self.screen.blit(textsurface,(400,0))
        
        if self.game.promotee:
            color = self.game.next_to_move
            pygame.draw.rect(self.screen, self.black, [700, 150, scale-20, scale-20], 1)
            sprite = Piece(self.screen, 700-3, 150-5, "Queen", color, self.sheet)
            sprite.blitme_small()
            pygame.draw.rect(self.screen, self.black, [700, 250, scale-20, scale-20], 1)
            sprite = Piece(self.screen, 700-3, 250-5, "Rook", color, self.sheet)
            sprite.blitme_small()
            pygame.draw.rect(self.screen, self.black, [700, 350, scale-20, scale-20], 1)
            sprite = Piece(self.screen, 700-3, 350-5, "Knight", color, self.sheet)
            sprite.blitme_small()
            pygame.draw.rect(self.screen, self.black, [700, 450, scale-20, scale-20], 1)
            sprite = Piece(self.screen, 700-3, 450-5, "Bishop", color, self.sheet)
            sprite.blitme_small()
        #vertical lines¨
        i = 0
        for x in range(self.width):
            for y in range(self.height):
                if self.game.board[x][y] == selected and selected != 0:
                    pygame.draw.rect(self.screen, self.green, [x*scale, (y)*scale, scale, scale])
                elif [x, y] in moves:
                    pygame.draw.rect(self.screen, self.blue, [x*scale, (y)*scale, scale, scale])
                elif (x + y) %2 == 1:
                    pygame.draw.rect(self.screen, self.black, [x*scale, (y)*scale, scale, scale])
                else:
                    pygame.draw.rect(self.screen, self.white, [x*scale, (y)*scale, scale, scale])
                if (self.game.board[x][y] != 0):
                    i += 1
                    piece = self.game.board[x][y] 
                    sprite = Piece(self.screen, x*scale-12, y*scale-10, piece.type, piece.color, self.sheet)
                    sprite.blitme()
                #if self.game.board[x][y] != 0:
                #    pygame.draw.circle(self.screen, self.green, [self.side_length + x*scale + 40, y * scale + 90], 40)
        pygame.event.pump()
        pygame.display.flip()
game = chess.Game()
GameRendering(game)