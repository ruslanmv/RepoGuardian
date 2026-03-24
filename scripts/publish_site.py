from repoguardian.site.generator import generate_site
from repoguardian.settings import get_settings

if __name__ == "__main__":
    generate_site(get_settings())
