import os
import glob

def clear_pyz():
    for pyz in glob.glob('*.pyz'):
        print(f'Clearing {pyz}.')
        os.remove(pyz)

    for zip in glob.glob('*.zip'):
        print(f'Clearing {zip}.')
        os.remove(zip)

if __name__ == "__main__":
    clear_pyz()
