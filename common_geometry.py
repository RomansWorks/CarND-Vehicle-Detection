
class Point():
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
        
    def scale(self, factor):
        return Point(self.x*factor, self.y*factor)
    
    def shift(self, dx, dy):
        return Point(self.x+dx, self.y+dy)
    
    def get_distance(self, other):
        return ((self.x-other.x)**2+(self.y-other.y)**2)**0.5

    def __repr__(self):
        return "Point({},{})".format(self.x,self.y)
    
class Rect():
    def __init__(self, p1, p2):
        assert p2.x >= p1.x
        assert p2.y >= p1.y
        self.p1 = p1
        self.p2 = p2

    def get_height(self):
        return self.p2.y - self.p1.y
    
    def get_width(self):
        return self.p2.x - self.p1.x
    
    def get_left(self):
        return self.p1.x
    
    def get_right(self):
        return self.p2.x
    
    def get_top(self):
        return self.p1.y
    
    def get_bottom(self):
        return self.p2.y
    
    def scale(self, factor):
        return Rect(self.p1.scale(factor), self.p2.scale(factor))
     
    def shift(self, dx, dy):
        return Rect(self.p1.shift(dx, dy), self.p2.shift(dx, dy))
    
    def calculate_overlap(self, other):
        left = max(self.get_left(), other.get_left())
        right = min(self.get_right(), other.get_right())
        top = max(self.get_top(), other.get_top())
        bottom = min(self.get_bottom(), other.get_bottom())
        if right - left <= 0 or bottom - top <= 0:
            return None
        else:
            return Rect(Point(left, top), Point(right, bottom))
        
    def calculate_area(self):
        return self.get_height() * self.get_width()
        
    def is_contained_in(self, other):
        return self.get_top() >= other.get_top() and self.get_bottom() <= other.get_bottom() and self.get_left() >= other.get_left() and self.get_right() <= other.get_right()
        
    def __repr__(self):
        return "Rect({},{})".format(self.p1,self.p2)    

    

def test_point():
    p = Point(10, 20)
    assert(p.x == 10)
    assert(p.y == 20)
    p_scaled = p.scale(5)
    assert(p_scaled.x == 50)
    assert(p_scaled.y == 100)
    p_shifted = p.shift(-10, 50)
    assert(p_shifted.x == 0)
    assert(p_shifted.y == 70)
    
    assert(p.get_distance(Point(10, 30)) == 10)
    assert(p.get_distance(Point(-10, 20)) == 20)
    
def test_rectangle():
    r = Rect(Point(0, 100), Point(50, 200))
    assert(r.p1.x == 0)
    assert(r.p1.y == 100)
    assert(r.p2.x == 50)
    assert(r.p2.y == 200)
    assert(r.get_height() == 100)
    assert(r.get_width() == 50)
    assert(r.calculate_area() == 5000)
    assert(r.get_left() == 0)
    assert(r.get_right() == 50)
    assert(r.get_top() == 100)
    assert(r.get_bottom() == 200)
    
    r_non_overlapping = Rect(Point(500, 500), Point(600, 600))
    assert(r.calculate_overlap(r_non_overlapping) == None)
    
    r_overlapping = Rect(Point(25, 150), Point(75, 250))
    overlap_rect = r.calculate_overlap(r_overlapping)
    overlap_area = overlap_rect.calculate_area()
    assert(overlap_area == 1250)
    
    # TODO: Test shift
    # TODO: Test scale
