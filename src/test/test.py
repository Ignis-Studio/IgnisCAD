from igniscad import *

if __name__ == "__main__":
    with Model("Robot") as model:
        with Group("Leg") as leg:
            foot = Box(20, 30, 5)
            pole = Cylinder(5, 40).on_top_of(foot)

            leg << pole << foot

        model << leg.move(x=-15) << leg.move(x=15)
        body = Box(50, 20, 38).on_top_of(model)
        model << body

    show(model)