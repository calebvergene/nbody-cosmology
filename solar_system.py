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
        
        self.energy_history = []
        self.total_steps = 0
        
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
                'trail_x': [], 'trail_y': [],
                'distance_from_sun': distance if name != "Sun" else 0,
                'orbital_period': np.sqrt(distance**3) if name != "Sun" else 0,
                'current_speed': speed if name != "Sun" else 0
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

    def calculate_total_energy(self):
        kinetic_energy = 0.0
        potential_energy = 0.0
        
        for body in self.bodies:
            speed_squared = body['vx']**2 + body['vy']**2
            kinetic_energy += 0.5 * body['mass'] * speed_squared
        
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                body1 = self.bodies[i]
                body2 = self.bodies[j]
                
                dx = body2['x'] - body1['x']
                dy = body2['y'] - body1['y']
                distance = np.sqrt(dx*dx + dy*dy)
                
                if distance > 0.01:
                    potential_energy -= self.G * body1['mass'] * body2['mass'] / distance
        
        return kinetic_energy + potential_energy
    
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
            
            if body['name'] != 'Sun':
                body['distance_from_sun'] = np.sqrt(body['x']**2 + body['y']**2)
                body['current_speed'] = np.sqrt(body['vx']**2 + body['vy']**2)
            
            # to animate the trail behind moving planet
            body['trail_x'].append(body['x'])
            body['trail_y'].append(body['y'])
            if len(body['trail_x']) > 500:
                body['trail_x'].pop(0)
                body['trail_y'].pop(0)

    def simulate_step(self, dt):
        self.update_positions(dt)
        self.time += dt
        self.total_steps += 1
        
        # just do energy conservation every 50 steps
        if self.total_steps % 50 == 0:
            energy = self.calculate_total_energy()
            self.energy_history.append((self.time, energy))
    
    def add_asteroid_belt(self, num_asteroids=20):
        """Add asteroids between Mars and Jupiter for more realistic n-body simulation"""
        
        for i in range(num_asteroids):
            distance = np.random.uniform(2.2, 3.3)  # Asteroid belt region
            angle = np.random.uniform(0, 2*np.pi)
            speed = np.sqrt(self.G * self.bodies[0]['mass'] / distance) * np.random.uniform(0.95, 1.05)
            
            x = distance * np.cos(angle)
            y = distance * np.sin(angle)
            vx = -speed * np.sin(angle)
            vy = speed * np.cos(angle)
            
            asteroid = {
                'name': f'Asteroid_{i+1}',
                'mass': np.random.uniform(1e-12, 1e-10),  # Very small masses
                'x': x, 'y': y,
                'vx': vx, 'vy': vy,
                'color': 'gray',
                'size': np.random.uniform(2, 5),
                'trail_x': [], 'trail_y': [],
                'distance_from_sun': distance,
                'orbital_period': np.sqrt(distance**3),
                'current_speed': speed
            }
            self.bodies.append(asteroid)
    
    def plot_energy_conservation(self):
        """plot energy over time to see physics accuracy"""
        if len(self.energy_history) < 2:
            return
            
        times = [data[0] for data in self.energy_history]
        energies = [data[1] for data in self.energy_history]
        
        initial_energy = energies[0]
        final_energy = energies[-1]
        energy_drift = abs((final_energy - initial_energy) / initial_energy) * 100
        
        plt.figure(figsize=(10, 6))
        plt.plot(times, energies, 'b-', linewidth=2, label='Total Energy')
        plt.xlabel('Time (years)')
        plt.ylabel('Total Energy')
        plt.title(f'Energy Conservation - Drift: {energy_drift:.4f}%')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
    
    #ANIMATING THE PLANETS IS SO HARD, got help from other git repo and integrated into this
    def create_animation(self, years=5, dt=0.01, show_asteroids=True):
        frames = []
        steps = int(years / dt)
        frame_skip = max(1, steps // 800)  # THIS IS TO CONTROL FRAME RATE, lower for less load
        
        for step in range(steps):
            self.simulate_step(dt)
            
            if step % frame_skip == 0:
                frame = {
                    'time': self.time,
                    'positions': [(body['x'], body['y']) for body in self.bodies],
                    'trails': [(body['trail_x'].copy(), body['trail_y'].copy()) for body in self.bodies],
                    'distances': [body.get('distance_from_sun', 0) for body in self.bodies],
                    'speeds': [body.get('current_speed', 0) for body in self.bodies]
                }
                frames.append(frame)
            
            if step % (steps // 10) == 0:
                progress = 100 * step / steps
                print(f"loading... {progress:.0f}%")
        
        fig = plt.figure(figsize=(15, 10))
        ax_main = plt.subplot2grid((3, 3), (0, 0), colspan=2, rowspan=3)
        ax_info = plt.subplot2grid((3, 3), (0, 2))
        ax_energy = plt.subplot2grid((3, 3), (1, 2))
        ax_distances = plt.subplot2grid((3, 3), (2, 2))
        
        fig.patch.set_facecolor('black')
        
        def animate_frame(frame_num):
            ax_main.clear()
            ax_info.clear()
            ax_energy.clear()
            ax_distances.clear()
            
            if frame_num >= len(frames):
                return
            
            frame = frames[frame_num]

            ####### This is where I incorporate the trails and planets ########
            
            ax_main.set_facecolor('black')
            
            for i, body in enumerate(self.bodies):
                if len(frame['trails'][i][0]) > 1:
                    trail_x, trail_y = frame['trails'][i]
                    alpha = 0.3 if body['name'].startswith('Asteroid') else 0.6
                    linewidth = 0.5 if body['name'].startswith('Asteroid') else 1.5
                    
                    if show_asteroids or not body['name'].startswith('Asteroid'):
                        ax_main.plot(trail_x, trail_y, color=body['color'], 
                                   alpha=alpha, linewidth=linewidth)
            
            for i, body in enumerate(self.bodies):
                x, y = frame['positions'][i]
                
                if not show_asteroids and body['name'].startswith('Asteroid'):
                    continue
                
                # add glow for sun lol
                if body['name'] == 'Sun':
                    ax_main.scatter(x, y, s=body['size']*2, c=body['color'], 
                            alpha=0.3, edgecolors='none')
                    ax_main.scatter(x, y, s=body['size'], c=body['color'], 
                            alpha=1.0, edgecolors='orange', linewidth=2)
                else:
                    size = body['size'] if not body['name'].startswith('Asteroid') else body['size']
                    ax_main.scatter(x, y, s=size, c=body['color'], 
                            alpha=0.9, edgecolors='white', linewidth=1)
                
                if not body['name'].startswith('Asteroid'):
                    ax_main.annotate(body['name'], (x, y), xytext=(8, 8), 
                            textcoords='offset points', color='white', 
                            fontsize=10, fontweight='bold')
            
            ax_main.set_xlim(-35, 35)
            ax_main.set_ylim(-35, 35)
            ax_main.set_xlabel('Distance (AU)', color='white', fontsize=12)
            ax_main.set_ylabel('Distance (AU)', color='white', fontsize=12)
            ax_main.set_title(f'N-Body Solar System - Year {frame["time"]:.2f}', 
                        color='white', fontsize=16, fontweight='bold')
            ax_main.grid(True, alpha=0.2, color='white')
            ax_main.set_aspect('equal')
            ax_main.tick_params(colors='white')
            
            ax_info.set_facecolor('black')
            info_text = f"N-BODY SIMULATION\n\n"
            info_text += f"Time: {frame['time']:.2f} years\n"
            info_text += f"Bodies: {len(self.bodies)}\n\n"
            
            for i in range(min(5, len(self.bodies))):
                if not self.bodies[i]['name'].startswith('Asteroid'):
                    body = self.bodies[i]
                    if body['name'] != 'Sun':
                        dist = frame['distances'][i]
                        speed = frame['speeds'][i]
                        info_text += f"{body['name']}:\n"
                        info_text += f"  {dist:.2f} AU\n"
                        info_text += f"  {speed:.2f} AU/yr\n\n"
            
            ax_info.text(0.05, 0.95, info_text, transform=ax_info.transAxes,
                        verticalalignment='top', fontfamily='monospace',
                        color='white', fontsize=8)
            ax_info.set_xlim(0, 1)
            ax_info.set_ylim(0, 1)
            ax_info.axis('off')
            
            if len(self.energy_history) > 1:
                times = [data[0] for data in self.energy_history]
                energies = [data[1] for data in self.energy_history]
                ax_energy.plot(times, energies, 'cyan', linewidth=1.5)
                ax_energy.set_ylabel('Energy', color='white', fontsize=8)
                ax_energy.set_title('Energy Conservation', color='white', fontsize=9)
                ax_energy.tick_params(colors='white', labelsize=6)
                ax_energy.set_facecolor('black')
            
            times_dist = [frame['time']] * min(8, len(self.bodies))
            distances_frame = frame['distances'][1:min(9, len(self.bodies))]  # Skip Sun
            colors = [self.bodies[i]['color'] for i in range(1, min(9, len(self.bodies)))]
            
            ax_distances.scatter(times_dist, distances_frame, c=colors, s=20, alpha=0.8)
            ax_distances.set_ylabel('Distance (AU)', color='white', fontsize=8)
            ax_distances.set_title('Planet Distances', color='white', fontsize=9)
            ax_distances.tick_params(colors='white', labelsize=6)
            ax_distances.set_facecolor('black')
        
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
    
    solar_system.add_asteroid_belt(num_asteroids=25)
    
    animation1 = solar_system.create_animation(years=3, dt=0.01, show_asteroids=True)
    
    solar_system.plot_energy_conservation()
    

    solar_system2 = SolarSystem()
    animation2 = solar_system2.create_inner_planets_view(years=2)