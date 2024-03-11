# NeuroJump - Machine Learning Jumping Game
NeuroJump is a simple machine learning-based jumping game developed using Pygame and NEAT (NeuroEvolution of Augmenting Topologies). The objective of the game is to train a generation of players to jump over tree obstacles using neural networks.

## How to Run
1. Run the game script (neurojump.py) to initialize the game window.
2. A generation of players will be spawned, each represented by an alien-looking character.
3. The players are controlled by neural networks that evolve over generations.
4. The game speed gradually increases, making it more challenging for players to avoid obstacles.
5. Players earn fitness points for staying alive and additional points for successfully avoiding obstacles.
6. The game continues until all players in a generation either hit an obstacle or the user closes the game window.

## Dependencies
- Python 3.x
- Pygame
- NEAT (NeuroEvolution of Augmenting Topologies)
## Installation
1. Clone the repository:
`git clone https://github.com/your-username/NeuroJump.git`
2. Install dependencies:
`pip install pygame neat-python`
3. Run the game:
`python NeuroJump.py`
## Configuration
The NEAT algorithm's parameters are defined in the config-feedforward.txt file. Adjust these settings to experiment with the evolutionary process.
