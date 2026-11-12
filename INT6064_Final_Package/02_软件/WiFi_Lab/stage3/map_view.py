import tkinter as tk
from data import CLASSROOMS, ROUTERS, ROUTER_COVERAGE, INSTALLATION_COSTS, COVERAGE_RADIUS, ROUTER_LIMIT

class MapView:
    def point(self, x, y):
            return 35 + x * 40, 420 - y * 40

    def draw_map(self):
    
            canvas = self.canvas
            canvas.delete("all")
    
            # Grid
    
            for i in range(10):
    
                x, _ = self.point(i, 0)
                _, y = self.point(0, i)
    
                canvas.create_line(
                    x, 60, x, 420,
                    fill="#dddddd"
                )
    
                canvas.create_line(
                    35, y, 395, y,
                    fill="#dddddd"
                )
    
                canvas.create_text(
                    x, 439,
                    text=str(i)
                )
    
                canvas.create_text(
                    27, y,
                    text=str(i)
                )
    
            # Coverage circles
    
            for router_id in self.selected:
    
                x, y = self.point(
                    *ROUTERS[router_id]
                )
    
                radius = COVERAGE_RADIUS * 40
    
                canvas.create_oval(
                    x-radius,
                    y-radius,
                    x+radius,
                    y+radius,
                    outline="#299764",
                    width=2,
                    dash=(5, 4)
                )
    
            covered = set()
    
            for router_id in self.selected:
                covered.update(
                    ROUTER_COVERAGE[router_id]
                )
    
            # Classrooms
    
            for classroom_id, position in CLASSROOMS.items():
    
                x, y = self.point(*position)
    
                if classroom_id in covered:
                    color = "#299764"
    
                elif len(self.selected) == ROUTER_LIMIT:
                    color = "#d9534f"
    
                else:
                    color = "#4477cc"
    
                canvas.create_oval(
                    x-7,
                    y-7,
                    x+7,
                    y+7,
                    fill=color,
                    outline="white"
                )
    
                canvas.create_text(
                    x,
                    y-18,
                    text=classroom_id,
                    font=("Arial", 9)
                )
    
            # Routers
    
            for router_id, position in ROUTERS.items():
    
                x, y = self.point(*position)
    
                selected = router_id in self.selected
    
                color = (
                    "#198754"
                    if selected
                    else "#c17c25"
                )
    
                tag = f"router_{router_id}"
    
                canvas.create_rectangle(
                    x-13,
                    y-13,
                    x+13,
                    y+13,
                    fill=color,
                    outline="#333333",
                    tags=(tag, "router")
                )
    
                canvas.create_text(
                    x,
                    y,
                    text=router_id,
                    fill="white",
                    font=("Arial", 10, "bold"),
                    tags=(tag, "router")
                )
    
                canvas.create_text(
                    x,
                    y+25,
                    text=(
                        f"${INSTALLATION_COSTS[router_id]}"
                    ),
                    font=("Arial", 9),
                    tags=(tag, "router")
                )
    
            canvas.tag_bind(
                "router",
                "<Button-1>",
                self.on_router_click
            )
