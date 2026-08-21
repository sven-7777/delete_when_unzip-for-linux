# Maintainer: sven-7777 <your-email@example.com>
pkgname=delete-when-unzip-git
_pkgname=delete_when_unzip-for-linux
pkgver=r56.69c33ce
pkgrel=1
pkgdesc="Extract large ZIP/RAR/TAR archives while deleting processed chunks, to avoid needing double disk space"
arch=('any')
url="https://github.com/sven-7777/delete_when_unzip-for-linux"
license=('MIT')
depends=('python' 'tk' 'libarchive' 'unrar' 'python-libarchive-c')
makedepends=('git' 'python-pip')
provides=('delete-when-unzip')
conflicts=('delete-when-unzip')
source=("$_pkgname::git+https://github.com/sven-7777/delete_when_unzip-for-linux.git")
sha256sums=('SKIP')

pkgver() {
    cd "$_pkgname"
    printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package() {
    cd "$_pkgname"

    # stream_unzip has no Arch/AUR package - vendor it into the app's own
    # directory via pip's --target, so it doesn't touch system site-packages.
    pip install --target "$pkgdir/usr/share/delete-when-unzip/vendor" \
        --no-deps --break-system-packages 'stream_unzip==0.0.88' 'stream-inflate>=0.0.12' 'pycryptodome>=3.10.1'

    install -d "$pkgdir/usr/share/delete-when-unzip"
    cp -r ./*.py "$pkgdir/usr/share/delete-when-unzip/"
    cp app_icon.png "$pkgdir/usr/share/delete-when-unzip/"

    install -Dm755 "$srcdir/../delete-when-unzip" "$pkgdir/usr/bin/delete-when-unzip"
    install -Dm755 "$srcdir/../delete-when-unzip-cli" "$pkgdir/usr/bin/delete-when-unzip-cli"

    install -Dm644 delete-when-unzip.desktop \
        "$pkgdir/usr/share/applications/delete-when-unzip.desktop"
    install -Dm644 app_icon.png \
        "$pkgdir/usr/share/icons/hicolor/32x32/apps/delete-when-unzip.png"

    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
