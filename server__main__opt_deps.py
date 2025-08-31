# Enable optional dependencies in server PYZ.
import sys
from server_pkg.server import main
sys.path.insert(0, "dependencies")
main(sys.argv[1:])
