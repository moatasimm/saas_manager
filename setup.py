from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="saas_manager",
    version="1.0.0",
    description="ERPNext SaaS Subscription Manager — لوحة إدارة اشتراكات SaaS",
    author="OpenTech",
    author_email="moatasim_m@yahoo.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
