# hover-drone

* Rajessen Sanassy, 101147410, rajessensanassy@cmail.carleton.ca
* Josh Kim, 101153583, joshkim3@cmail.carleton.ca
* Shirwa Jama, 101155370, shirwajama@cmail.carleton.ca
* Osman Mohamed, 101142431, osmanimohamed@cmail.carleton.ca
* Jovin Bains, 101147412, jovinbains@cmail.carleton.ca


## create environement
`python3 -m venv venv`
## activate environement
Mac: `source venv/bin/activate`<br>
Windows: `/venv/Scripts/activate` or `/venv/Scripts/Activate.ps1` if running on powershell

## install requirements
`pip3 install -r requirements.txt`

## run playable game
`python3 simulate.py`<br>
`python3 simulate.py -m human`

## run gym environment game (model actions)
`python3 simulate.py -m model_QRDQN`<br>
`python3 simulate.py -m model_PPO`<br>
`python3 simulate.py -m model_SAC`<br>
`python3 simulate.py -m model_TQC_1`<br>
`python3 simulate.py -m model_TQC_2`<br>

## run training in gym environment game
`python3 train.py -m DQN`<br>
`python3 train.py -m QRDQN`<br>
`python3 train.py -m PPO`<br>
`python3 train.py -m SAC`<br>
`python3 train.py -m TQC`<br>
