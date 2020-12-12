import tkinter as tk
#self 類似java中的this，java中有宣告變數，因此不一定要使用this,但python沒有宣告，self能當作該"類別自身"的全域變數
class Gameobject(object):#球、磁磚、踏板的父類
       def __init__(self, canvas, item):
              self.canvas = canvas
              self.item = item
       def get_position(self):
              return self.canvas.coords(self.item)
       def move(self, x, y):
              self.canvas.move(self.item, x, y)
       def delete(self): 
              self.canvas.delete(self.item)
              
class Ball(Gameobject):#定義球
       def __init__(self, canvas, x, y):
              radius = 10
              self.speed=3
              self.direction=[1,-1]#反彈方位 
              item=canvas.create_oval(x-radius, y-radius,
                                      x+radius, y+radius,
                                      fill="white")
              super().__init__(canvas, item)

       def update(self):
              coords = self.get_position()
              width = self.canvas.winfo_width()
 
              if coords[0] <= 0 or coords[2] >= width:
                  self.direction[0] *= -1
              if coords[1] <= 0:
                  self.direction[1] *= -1
              x = self.direction[0] * self.speed
              y = self.direction[1] * self.speed
              self.move(x, y)
       def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()       
class Paddle(Gameobject):#定義踏板
       def __init__(self,canvas, x, y):
              self.width=80
              self.height=10
              self.ball=None
              item=canvas.create_rectangle(x - self.width/2,
                                           y - self.height/2,
                                           x + self.width/2,
                                           y + self.height/2,
                                           fill="blue") #item為int 表物件的編號，每create新物件就會自動加1
              super().__init__(canvas, item)
       def set_ball(self, ball):
              self.ball = ball
       def move(self,offset):
           coord = self.get_position()
           width = self.canvas.winfo_width()
           if(coord[0]+offset>=0 and coord[2]+offset<=width):
               super().move(offset,0)
               if self.ball is not None:
                   self.ball.move(offset,0)
              
class Brick(Gameobject):
       COLORS={1:"#999999", 2:"#555555", 3:"#222222"}
       def __init__(self,canvas, x, y, hits):
              self.width = 75
              self.height = 20
              self.hits = hits
              color = Brick.COLORS[self.hits]
              item=canvas.create_rectangle(x - self.width/2,
                                           y - self.height/2,
                                           x + self.width/2,
                                           y + self.height/2,
                                           fill = color,
                                           tags = "brick")
              
              super().__init__(canvas, item) 
       
       def hit(self):
              self.hits-=1
              if(self.hits==0):
                     self.delete()
              else:
                     self.canvas.itemconfig(self.item,fill=Brick.COLORS[self.hits])
                     
class Game(tk.Frame):#主視窗
       def __init__(self,root):
              super().__init__(root)#Frame 需繼承tkinter
              self.lives  = 3
              self.width  = 610
              self.height = 400
              self.canvas = tk.Canvas(self, width = self.width, height = self.height, bg="#aaaaff")
              
              
              self.canvas.pack()
              self.pack()

              self.item = {}
              self.ball = None
              self.paddle = Paddle(self.canvas,310,326)#初始化踏板
              self.item[self.paddle.item] = self.paddle
              for x in range(5, self.width-5,75):
                     self.add_brick(x+37.5, 50 , 3)
                     self.add_brick(x+37.5, 70 , 2)
                     self.add_brick(x+37.5, 90 , 1)
              
              self.textitem= None
              self.setup_game()
              self.canvas.focus_set()#綁定鍵盤
              self.canvas.bind("<Left>",lambda _:self.paddle.move(-20))
              self.canvas.bind("<Right>",lambda _:self.paddle.move(20))
       def setup_game(self):
              self.add_ball()
              self.update_lives_text()
              self.text = self.canvas.create_text(300 ,200,text='Press Space to start',font=("Helvetica",40))
              self.canvas.bind("<space>",self.start_game)
       def add_brick(self, x, y, hits):
              brick = Brick (self.canvas, x, y, hits)
              self.item[brick.item] = brick
       def add_ball(self):
              paddle_coords = self.paddle.get_position()
              x = (paddle_coords[0]+ paddle_coords[2])/2
              if self.ball is not None:
                     self.ball.delete()
              self.ball = Ball(self.canvas, x, paddle_coords[1]-11)
              self.paddle.set_ball(self.ball)
       def update_lives_text(self):
              text1 = "Live is %s" % self.lives
              if(self.textitem == None):
                  self.textitem = self.canvas.create_text(50 ,20 ,text=text1,font=("Helvetica",15))
       def start_game(self,event):
              self.canvas.unbind('<space>')
              self.canvas.delete(self.text)
              self.paddle.ball = None
              self.game_loop()
       def game_loop(self):
              self.check_collisions()
              num_bricks = len(self.canvas.find_withtag('brick'))
              if num_bricks == 0: 
                  self.ball.speed = None
                  self.draw_text(300, 200, 'You win!')
              elif self.ball.get_position()[3] >= self.height: 
                  self.ball.speed = None
                  self.lives -= 1
                  if self.lives < 0:
                      self.draw_text(300, 200, 'Game Over')
                  else:
                      self.after(1000, self.setup_game)
              else:
                  self.ball.update()
                  self.after(17, self.game_loop)
       def check_collisions(self):
              ball_coords = self.ball.get_position()
              #overlapping 回傳被指定矩形重疊或完全包圍的項目，回傳物件編號 (球必定與自己碰撞故回傳球的id，此處是26)
              items = self.canvas.find_overlapping(*ball_coords)
              objects = [self.item[x] for x in items if x in self.item]
              self.ball.collide(objects)
if __name__ == "__main__":
       root = tk.Tk()
       root.resizable(False, False)
       root.title("小遊戲")
       game = Game(root)
       root.mainloop()      #IDLE本身就有互動功能、維持視窗 因此可加可不加(cmd執行必須加)
       
