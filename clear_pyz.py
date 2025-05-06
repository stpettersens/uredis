import os
import glob

def clear_pyz():
    for pyz in glob.glob('*.pyz'):
        print(f'Clearing {pyz}.')
        os.remove(pyz)

if __name__ == "__main__":
    clear_pyz()
