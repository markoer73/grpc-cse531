cd ..
virtualenv grpc 2&>/dev/null
source grpc/bin/activate
cd grpc/CSE531

#python3 -m pdb Main.py -i test1.json -o output.json

# Test 1
#python3 Main.py -i test1.json -o output1.json

# Test 2
python3 Main.py -i test2.json -o output2.json
