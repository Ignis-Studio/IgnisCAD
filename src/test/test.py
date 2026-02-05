from igniscad import *

if __name__ == "__main__":
    with Item("Robot") as item:
        with Group("Leg") as leg:
            foot = Box(20, 30, 5)
            pole = Cylinder(5, 40).on_top_of(foot)

            leg << pole << foot

        item << leg.move(x=-15) << leg.move(x=15)

    show(item)