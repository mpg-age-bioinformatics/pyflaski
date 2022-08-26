# pyflaski

This the Graphical User Interface to Programmatic Interface helper package of Flaski.

![flaski](/Flaski.Readme.png)

## Installing 

```bash
git clone https://github.com/mpg-age-bioinformatics/pyflaski
cd pyflaski
pip3 install -r requirements.txt --user
pip3 install . --user
```

## Using the docker image

```bash
mkdir ~/pyflaski_sessions
docker run -v ~/pyflaski_sessions:/pyflaski_sessions -p 8989:8989 -it mpgagebioinformatics/pyflaski jupyter lab --allow-root --ip=0.0.0.0 --port=8989
```

Check out the example notebook [ipynb](example.ipynb)/[html](example.html)/[pdf](example.pdf).