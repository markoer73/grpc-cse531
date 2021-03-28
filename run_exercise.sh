cd ..
virtualenv grpc 2&>/dev/null
source grpc/bin/activate
cd grpc/CSE531

#python3 -m pdb Main.py -i test1.json -o output.json
python3 Main.py -i test1.json -o output.json

