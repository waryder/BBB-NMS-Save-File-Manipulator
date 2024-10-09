import json

# 1. Static JSON string
json_string = """[
	{
		"BaseVersion":8,
		"OriginalBaseVersion":5,
		"GalacticAddress":52819506714175,
		"Position":[
			0.0,
			0.0,
			0.0
		],
		"Forward":[
			0.2935546934604645,
			0.5539793372154236,
			-0.7790588140487671
		],
		"UserData":0,
		"LastUpdateTimestamp":1727155547,
		"Objects":[
			{
				"Timestamp":1727156441,
				"ObjectID":"^FRE_ROOM_IND",
				"UserData":51,
				"Position":[
					0.000030517578125,
					4.000070571899414,
					19.500091552734376
				],
				"Up":[
					87.42271262462964E-9,
					1.0,
					-476.837158203125E-9
				],
				"At":[
					-150.99583094979608E-9,
					-476.837158203125E-9,
					-1.0
				],
				"Message":""
			},
			{
				"Timestamp":1727156441,
				"ObjectID":"^FRE_ROOM_IND",
				"UserData":51,
				"Position":[
					0.0000457763671875,
					4.00007438659668,
					27.500152587890626
				]
			}
		]
	}	
]"""

# 2. Use json.loads() to parse the JSON string into a Python dictionary
parsed_json = json.loads(json_string)

# 3. Convert the Python dictionary back to a JSON string using json.dumps()
json_output = json.dumps(parsed_json, indent=4, separators=(', ', ':\n'))

# 4. Print the variable to the console
print("JSON Output:")
print(json_output)