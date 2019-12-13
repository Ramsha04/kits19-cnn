from setuptools import setup, find_packages

setup(name="kits19cnn",
      version="0.01.5",
      description="Submission for the KiTS 2019 Challenge",
      url="https://github.com/jchen42703/kits19-cnn",
      author="Joseph Chen, Benson Jin",
      author_email="jchen42703@gmail.com, jinb2@bxsci.edu",
      license="Apache License Version 2.0, January 2004",
      packages=find_packages(),
      install_requires=[
            "numpy>=1.10.2",
            "scipy",
            "scikit-image",
            "future",
            "keras",
            "tensorflow",
            "nibabel",
            "pandas",
            "sklearn",
            "batchgenerators",
            "torch>=1.2.0",
            "torchvision>=0.4.0",
            "catalyst",
            "pytorch_toolbelt",
            "segmentation_models_pytorch==0.1.0",
      ],
      classifiers=[
          "Development Status :: 3 - Alpha",
          # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
          "Intended Audience :: Developers",  # Define that your audience are developers
          "Topic :: Software Development :: Build Tools",
          "License :: OSI Approved :: MIT License",  # Again, pick a license
          "Programming Language :: Python :: 3",  # Specify which python versions that you want to support
          "Programming Language :: Python :: 3.6",
      ],
      keywords=["deep learning", "image segmentation", "image classification", "medical image analysis",
                 "medical image segmentation", "data augmentation"],
      )
