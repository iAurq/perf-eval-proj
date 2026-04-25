# Performance Evaluation and Benchmarking (ECE 382N.21)
Final Project in 382N.21 Performance Evaluation &amp; Benchmarking Class w/ Dr. Lizy John

# heaven.py
This file contains a script to automatically run the free (gamer) version of 
Heaven on a Windows system.

Please download all the necessary libraries using the `requirements.txt` file.

## .env
For this program to work you must create a `.env` file in the root directory of this repo. It must contain the following:
```dotenv
HEAVEN_PATH=<PATH_TO_HEAVEN>
```

## Other General Limitations
Some aspects of the script are timing based (for example waiting for the heaven launcher to display on screen). Please
go through the file and adjust any lines with the `FIXME` comment to your timing needs.


# power.py
This file contains a class to start a `nvidia-smi` background process to log power.

## Limitations
It currently uses the default ~1s time to poll for power. I (Yahir) left as because as you increase the polling rate,
you increase the overhead [link](https://forums.developer.nvidia.com/t/is-there-sample-period-change-available-for-nvidia-smi/203656/2). 
Not sure if it's worth the tradeoff. 