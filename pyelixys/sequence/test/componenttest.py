from pyelixys.sequence import comp_lookup

class db:
    pass

add_details = {}
add_details['reactor'] = 0
add_details['sequenceid'] = 0
add_details['reagentpos'] = 5
add_details['componentid'] = 0
add_details['deliverytime'] = 5.0
add_details['deliveryposition'] = 0.0
add_details['deliverypressure'] = 3.0
add_details['note'] = "Add from reactor 0 position 3 to add 0"

db.details = add_details

add = comp_lookup['ADD'](db)

#add.run()
#add.reactor = add.system.reactors[1]
#add.reagent_pos = 3
#add.run()
    
elute_details = {}
elute_details['reactor'] = 0
elute_details['sequenceid'] = 0
elute_details['reagentpos'] = 5
elute_details['id'] = 0
elute_details['elutetime'] = 2.0
elute_details['elutepressure'] = 3.0
elute_details['note'] = "Elute from reactor 0 position 5 to add"

db.details = elute_details

elute = comp_lookup['ELUTEF18'](db)

evaporate_details = {}
evaporate_details['duration'] = 15
evaporate_details['evaporationpressure'] = 10
evaporate_details['evaporationtemperature'] = 55
evaporate_details['finaltemperature'] = 50.0
evaporate_details['reactor'] = 0
evaporate_details['stirspeed'] = 50.0
evaporate_details['coolduration'] = 5.0
evaporate_details['sequenceid'] = 14
evaporate_details['componentid'] = 0 
evaporate_details['note'] = '' 


db.details = evaporate_details

evaporate = comp_lookup['EVAPORATE'](db)

initialize_details = {}
initialize_details["note"] = ""
initialize_details["sequenceid"] = 0
initialize_details['id'] = 1

db.details = initialize_details

initialize = comp_lookup['INITIALIZE'](db)

install_details["sequenceid"] = 14
install_details[["reactor"] = 2
install_details[["note"] = ""
install_details[["message"] = ""
install_details[["id"] = 107

db.details = install_details

install = comp_lookup['INSTALL'](db)

mix_details["time"] = 10,
mix_details["componenttype"] = "MIX"
mix_details["reactor"] = 0 
mix_details["stirspeed"] = 100.0 
mix_details["sequenceid"] = 14
mix_details["note"] = "",
mix_details["type"] = "component" 
mix_details["componentid"] = 112

db.details = mix_details

mix = comp_lookup['MIX'](db)

react_details['reactor'] = 0
react_details['sequenceid'] = 0
react_details['componentid'] = 0
react_details['stirpeed'] = 50
react_details['duration'] = 10 
react_details['reactiontemperature'] = 55
react_details['coolduration'] = 120
react_details['coolingdelay'] = True
react_details['note'] = ""

db.details = react_details

react = comp_lookup['react'](db)

transfer_details['componentid'] = 0
transfer_details['sequenceid'] = 0
transfer_details['sourcereactor'] = 0
transfer_details['targetreactor'] = 1
transfer_details['duration'] = 5.0
transfer_details['deliveryposition'] = 0
transfer_details['pressure'] = 3.0
transfer_details['mode'] = None
transfer_details['note'] = "Transferring from Reactor 1 to Reactor 2"

db.details = transfer_details

transfer - comp_lookup['transfer'](db)




if __name__ == '__main__': 
    from IPython import embed
    embed()
    