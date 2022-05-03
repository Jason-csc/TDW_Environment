"""tdweb development configuration."""
import pathlib
# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'
# Secret key for encrypting cookies
SECRET_KEY = b'\xba\xf0x\xf3\x92Ol\xad\x9a\x18\xcb\x88\xd3\xe35=\xb7\xbdZ\xdf5\xab1/'
SESSION_COOKIE_NAME = 'login'
# File Upload to var/uploads/
tdweb_ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = tdweb_ROOT/'var'/'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

DATABASE_FILENAME = tdweb_ROOT/'var'/'tdweb.sqlite3'