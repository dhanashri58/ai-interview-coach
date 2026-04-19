import random
from typing import List, Dict, Union, Tuple, Optional

class WumpusInterviewWorld:
    def __init__(self, questions: list, profile: dict):
        self.grid_size = 4
        self.agent_pos = (0, 0)
        self.visited = {(0, 0)}
        self.kb = ["Initial State: Start at (0,0). SAFE."]
        self.safe_cells = {(0, 0)}
        self.wumpus_cells = set()
        self.pit_cells = set()
        self.gold_cell = (3, 3) 
        self.grid = self._generate_grid(questions)
        self.percepts = {} # (row, col) -> ["stench", "breeze", "glitter"]

    def _generate_grid(self, questions):
        grid = {}
        all_cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
        all_cells.remove((0, 0)) # Never at start
        
        non_start = list(all_cells)
        near_start = [(0, 1), (1, 0)]
        safe_non_start = [c for c in non_start if c not in near_start]
        
        random.shuffle(safe_non_start)
        
        # Assign hazards and gold using indices
        self.wumpus_cells.add(safe_non_start[0])
        self.wumpus_cells.add(safe_non_start[1])
        self.pit_cells.add(safe_non_start[2])
        self.pit_cells.add(safe_non_start[3])
        self.pit_cells.add(safe_non_start[4])
        self.gold_cell = safe_non_start[5]
        
        # Populate with questions
        q_pool = list(questions)
        random.shuffle(q_pool)
        
        q_ptr = 0
        grid[(0, 0)] = q_pool[q_ptr] if q_ptr < len(q_pool) else {"question": "Default Intro", "id": "0"}
        q_ptr += 1
        
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if (r, c) == (0, 0): continue
                if q_ptr < len(q_pool):
                    grid[(r, c)] = q_pool[q_ptr]
                    q_ptr += 1
                else:
                    grid[(r, c)] = {"question": f"Topic question at ({r},{c})", "id": f"q_{r}_{c}"}
        return grid

    def get_percept(self, pos):
        r, c = pos
        p = []
        # Check neighbors for hazards
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if (nr, nc) in self.wumpus_cells: p.append("stench")
            if (nr, nc) in self.pit_cells: p.append("breeze")
        if pos == self.gold_cell: p.append("glitter")
        return p

    def update_kb(self, pos):
        p = self.get_percept(pos)
        self.percepts[pos] = p
        
        if not p:
            self.kb.append(f"Cell {pos}: No breeze, no stench → Adjacent cells are SAFE.")
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = pos[0] + dr, pos[1] + dc
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                    self.safe_cells.add((nr, nc))
        else:
            if "stench" in p:
                self.kb.append(f"Cell {pos}: Stench detected! Wumpus adjacent.")
            if "breeze" in p:
                self.kb.append(f"Cell {pos}: Breeze detected! Pit adjacent.")
            if "glitter" in p:
                self.kb.append(f"Cell {pos}: Glitter detected! Found GOLD.")

    def choose_next_cell(self):
        unvisited_safe = self.safe_cells - self.visited
        if unvisited_safe:
            target = list(unvisited_safe)[0]
            return target
        
        all_cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
        unknown = [c for c in all_cells if c not in self.visited]
        if unknown:
            return random.choice(unknown)
        return None

    def move_agent(self, pos):
        self.agent_pos = pos
        self.visited.add(pos)
        self.update_kb(pos)
        
        effect = "normal"
        if pos in self.wumpus_cells: effect = "wumpus"
        elif pos in self.pit_cells: effect = "pit"
        elif pos == self.gold_cell: effect = "gold"
        
        return self.grid.get(pos), effect

    def get_grid_html(self):
        html = '<table style="border-collapse: collapse; margin: 10px auto; background: #0A0A10; color: white; border: 1px solid #333; width: 240px; height: 240px;">'
        for r in range(self.grid_size):
            html += '<tr style="height: 60px;">'
            for c in range(self.grid_size):
                pos = (r, c)
                content = "?"
                cell_style = "width: 60px; height: 60px; text-align: center; border: 1px solid #444;"
                
                if pos == self.agent_pos:
                    content = "🤖"
                    cell_style += "background: rgba(0, 212, 170, 0.2); border: 2px solid #00d4aa;"
                elif pos in self.visited:
                    if pos in self.wumpus_cells: content = "💀"
                    elif pos in self.pit_cells: content = "⚫"
                    elif pos == self.gold_cell: content = "💰"
                    else: content = "✅"
                    cell_style += "background: rgba(255, 255, 255, 0.05);"
                
                html += f'<td style="{cell_style}">{content}</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def get_kb_log(self):
        return self.kb
