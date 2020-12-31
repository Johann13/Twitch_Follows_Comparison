# TODO Provide channel ids and names
# list of channel (id,name)
channel_list: [(str, str)] = [
    ('15597175', 'alsmiffy'),
    ('219068259', 'AngoryTom'),

    ('91904368', 'bobawitch'),

    ('145983935', 'Bekkiboom'),
    ('150004439', 'bedgars'),
    ('52172280', 'bokoen'),
    ('113954840', 'bouphe'),
    ('64758947', 'Breeh'),
    ('79911474', 'brionykay'),

    ('63839894', 'Checkpoint'),

    ('21285936', 'Daltos'),

    ('44135610', 'FionaRiches'),

    ('87245015', 'Geestargames'),

    ('21945983', 'HatFilms'),
    ('197603698', 'highrollersdnd'),
    ('27063689', 'hrry'),

    ('12131870', 'InTheLittleWood'),
    ('91990032', 'ispuuuv'),

    ('40639871', 'JoeHickson'),

    ('26574506', 'Lalna'),
    ('71290568', 'Leoz'),

    ('465613748', 'm4ngo'),
    ('62904151', 'MiniMuka'),
    ('46969360', 'Mousie'),

    ('43903804', 'NanoKim'),
    ('21615575', 'Nilesy'),

    ('24070690', 'Pedguin'),
    ('19309473', 'Pyrionflax'),

    ('38167015', 'Ravs_'),
    ('37569443', 'Rimmy'),
    ('239617169', 'Rossperu'),
    ('22168131', 'Rythian'),

    ('38180017', 'Sherlock_Hulmes'),
    ('21069037', 'simonhoneydew'),
    ('26538483', 'sips_'),
    ('62568743', 'SquidGame'),

    ('42314834', 'TheRambler146'),
    ('141902679', 'thespiffingbrit'),

    ('43903922', 'Vadact'),
    ('96502692', 'WilsonatorYT'),
    ('416016021', 'YogCon'),
    ('20786541', 'Yogscast'),
    ('38051463', 'ZoeyProasheck'),
    ('31883069', 'Zylush'),
]

# converting the list to a map
channel_map: {str: str} = {c[0]: c[1] for c in channel_list}

# list of channel ids
channel_ids = list(map(lambda c: c[0], channel_list))

# id of the channel you want to compare two
main_channel_id: str = ''
