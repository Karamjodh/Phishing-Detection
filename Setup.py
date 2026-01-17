from setuptools import find_packages,setup
from typing import List

def get_requirements()-> List[str]:
    """
    This Function will return List of Requirements

    """
    requirement_lst =[]
    try:
        with open("requirements.txt","r") as file:
            lines = file.readlines()
            for line in lines:
                requirement = line.strip()
                if requirement and requirement != "-e .":
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("Requirements.txt file not found")

    return requirement_lst

setup(
    name = "Network Security",
    version = "0.0.1",
    author = "Karamjodh Singh",
    author_email = "rattan5650@gmail.com",
    packages = find_packages(),
    install_requires = get_requirements() 
)