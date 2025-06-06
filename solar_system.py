import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

# This will be the god class for the project. Object for solar system.
class SolarSystem:
    def __init__(self):
        # gravitational constant
        self.G = 4 * np.pi**2
        
        # for each planet
        self.bodies = self.create_planets()
        self.time = 0.0
        
    def create_planets(self):
        """
        create the planets in the solar system with their initial positions, velocities, and properties.
        - returns:
            list: a list of dictionaries. each dict is a planet.
        """
        # [name, mass, distance from sun, orbit speed, color, size] tried to get measuremnts similar to real solar system
        planet_data = [
            ["Sun",     1.0,      0.0,   0.0,   "gold",      300],
            ["Mercury", 1.66e-7,  0.39,  9.8,   "gray",      20],
            ["Venus",   2.45e-6,  0.72,  7.4,   "orange",    25],
            ["Earth",   3.0e-6,   1.0,   6.3,   "blue",      25],
            ["Mars",    3.23e-7,  1.5,   5.1,   "red",       22],
            ["Jupiter", 9.55e-4,  5.2,   2.8,   "brown",     100],
            ["Saturn",  2.86e-4,  9.5,   2.0,   "goldenrod", 90],
            ["Uranus",  4.37e-5,  19.2,  1.4,   "lightblue", 50],
            ["Neptune", 5.15e-5,  30.1,  1.1,   "darkblue",  50]
        ]
        
        bodies = []
        for name, mass, distance, speed, color, size in planet_data:
            angle = np.random.uniform(0, 2*np.pi) if name != "Sun" else 0
            
            # (x, y coordinates)
            x = distance * np.cos(angle)
            y = distance * np.sin(angle)
            
            if name == "Sun":
                vx, vy = 0.0, 0.0
            else:
                vx = -speed * np.sin(angle)
                vy = speed * np.cos(angle)
            
            body = {
                'name': name,
                'mass': mass,
                'x': x, 
                'y': y,
                'vx': vx, 
                'vy': vy,
                'color': color,
                'size': size,
                'trail_x': [], 'trail_y': []
            }
            bodies.append(body)
        
        return bodies
    
    def calculate_forces(self):
        """
        calculate the gravitational forces between all pairs of bodies in the solar system.
        this method updates the force components (fx, fy) for each body based on the gravitational interaction with every other body.
        """
        for body in self.bodies:
            body['fx'] = 0.0
            body['fy'] = 0.0
        
        # now calc force between each pair of planets
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                body1 = self.bodies[i]
                body2 = self.bodies[j]
                
                # get distance between the planets
                dx = body2['x'] - body1['x']
                dy = body2['y'] - body1['y']
                distance = np.sqrt(dx*dx + dy*dy)
                
                # ERROR NEED TO FIX: division by zero?
                if distance < 0.01:
                    distance = 0.01
                
                force = self.G * body1['mass'] * body2['mass'] / (distance**3)
                fx = force * dx
                fy = force * dy
                # update forces for both bodies
                body1['fx'] += fx
                body1['fy'] += fy
                body2['fx'] -= fx
                body2['fy'] -= fy
    
    def update_positions(self, dt):
        """updates positions and velocities each frame of animation"""
        self.calculate_forces()
        
        for body in self.bodies:
            # get acceleration for each planet
            ax = body['fx'] / body['mass']
            ay = body['fy'] / body['mass']
            
            # now velocity
            body['vx'] += ax * dt
            body['vy'] += ay * dt
            
            # now position
            body['x'] += body['vx'] * dt
            body['y'] += body['vy'] * dt
            
            # to animate the trail behind moving planet
            body['trail_x'].append(body['x'])
            body['trail_y'].append(body['y'])
            if len(body['trail_x']) > 500:
                body['trail_x'].pop(0)
                body['trail_y'].pop(0)

    def simulate_step(self, dt):
        self.update_positions(dt)
        self.time += dt
    
    #ANIMATING THE PLANETS IS SO HARD, got help from other git repo and integrated into this
    def create_animation(self, years=5, dt=0.01):
        frames = []
        steps = int(years / dt)
        frame_skip = max(1, steps // 800)  # THIS IS TO CONTROL FRAME RATE, lower for less load
        
        for step in range(steps):
            self.simulate_step(dt)
            
            if step % frame_skip == 0:
                frame = {
                    'time': self.time,
                    'positions': [(body['x'], body['y']) for body in self.bodies],
                    'trails': [(body['trail_x'].copy(), body['trail_y'].copy()) for body in self.bodies]
                }
                frames.append(frame)
            
            if step % (steps // 10) == 0:
                progress = 100 * step / steps
                print(f"loading... {progress:.0f}%")
        
        fig, ax = plt.subplots(figsize=(12, 12))
        fig.patch.set_facecolor('black')
        
        def animate_frame(frame_num):
            ax.clear()
            ax.set_facecolor('black')
            
            if frame_num >= len(frames):
                return
            
            frame = frames[frame_num]

            ####### This is where I incorporate the trails and planets ########
            
            for i, body in enumerate(self.bodies):
                if len(frame['trails'][i][0]) > 1:
                    trail_x, trail_y = frame['trails'][i]
                    ax.plot(trail_x, trail_y, color=body['color'], 
                        alpha=0.6, linewidth=1.5)
            
            for i, body in enumerate(self.bodies):
                x, y = frame['positions'][i]
                
                # add glow for sun lol
                if body['name'] == 'Sun':
                    ax.scatter(x, y, s=body['size']*2, c=body['color'], 
                            alpha=0.3, edgecolors='none')
                    ax.scatter(x, y, s=body['size'], c=body['color'], 
                            alpha=1.0, edgecolors='orange', linewidth=2)
                else:
                    ax.scatter(x, y, s=body['size'], c=body['color'], 
                            alpha=0.9, edgecolors='white', linewidth=1)
                
                # names above planets
                ax.annotate(body['name'], (x, y), xytext=(8, 8), 
                        textcoords='offset points', color='white', 
                        fontsize=10, fontweight='bold')
            
            ax.set_xlim(-35, 35)
            ax.set_ylim(-35, 35)
            ax.set_xlabel('Distance (AU)', color='white', fontsize=12)
            ax.set_ylabel('Distance (AU)', color='white', fontsize=12)
            ax.set_title(f'Solar System Simulation - Year {frame["time"]:.2f}', 
                        color='white', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.2, color='white')
            ax.set_aspect('equal')
            ax.tick_params(colors='white')
            info_text = f"time: {frame['time']:.2f} years\n"
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                color='white', fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        anim = FuncAnimation(fig, animate_frame, frames=len(frames), 
                        interval=50, repeat=True, blit=False)
        
        plt.tight_layout()
        plt.show()
        return anim
    
    # Important to note: this is a special function derived from the first to allow for a second view of the orbit. 
    # It was hard to make the distance ratio from the sun of each planet accurate without either having the farther 
    # planets off screen or the closer ones overlapping with the sun. So, I just did to seperate animations, 
    # one zoomed out and the other zoomed in. 
    def create_inner_planets_view(self, years=2):
        frames = []
        steps = int(years / 0.005)
        frame_skip = max(1, steps // 500)
        
        for step in range(steps):
            self.simulate_step(0.005)
            
            if step % frame_skip == 0:
                frame = {
                    'time': self.time,
                    'positions': [(body['x'], body['y']) for body in self.bodies[:5]],
                    'trails': [(body['trail_x'].copy(), body['trail_y'].copy()) for body in self.bodies[:5]]
                }
                frames.append(frame)
        
        fig, ax = plt.subplots(figsize=(10, 10))
        fig.patch.set_facecolor('black')
        
        def animate_inner(frame_num):
            ax.clear()
            ax.set_facecolor('black')
            
            if frame_num >= len(frames):
                return
            
            frame = frames[frame_num]
            
            for i in range(5):
                body = self.bodies[i]
                if len(frame['trails'][i][0]) > 1:
                    trail_x, trail_y = frame['trails'][i]
                    ax.plot(trail_x, trail_y, color=body['color'], 
                        alpha=0.7, linewidth=2)
            
            for i in range(5):
                body = self.bodies[i]
                x, y = frame['positions'][i]
                
                if body['name'] == 'Sun':
                    ax.scatter(x, y, s=body['size'], c=body['color'], 
                            alpha=1.0, edgecolors='orange', linewidth=2)
                else:
                    ax.scatter(x, y, s=body['size']*1.5, c=body['color'], 
                            alpha=0.9, edgecolors='white', linewidth=1)
                
                ax.annotate(body['name'], (x, y), xytext=(8, 8), 
                        textcoords='offset points', color='white', 
                        fontsize=12, fontweight='bold')
            
            ax.set_xlim(-2.5, 2.5)
            ax.set_ylim(-2.5, 2.5)
            ax.set_xlabel('Distance (AU)', color='white', fontsize=12)
            ax.set_ylabel('Distance (AU)', color='white', fontsize=12)
            ax.set_title(f'Inner Solar System - Year {frame["time"]:.2f}', 
                        color='white', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3, color='white')
            ax.set_aspect('equal')
            ax.tick_params(colors='white')
        
        anim = FuncAnimation(fig, animate_inner, frames=len(frames), 
                        interval=50, repeat=True, blit=False)
        
        plt.tight_layout()
        plt.show()
        return anim

if __name__ == "__main__":   
    solar_system = SolarSystem()
    animation1 = solar_system.create_animation(years=3, dt=0.01)
    solar_system2 = SolarSystem()
    animation2 = solar_system2.create_inner_planets_view(years=2) 