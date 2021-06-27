from src.commander.element.LyricsEmbed import LyricsEmbed


def test_fields():
    kwargs = {"lyrics": "Test", "lyrics_source": "Source: LyricFind"}
    embed_object = LyricsEmbed(**kwargs)
    assert embed_object.title == "Lyrics"
    assert embed_object.description == "Test"
    assert embed_object.footer.text == "Source: LyricFind"


def test_lyrics_bob():
    kwargs = {
        "lyrics": "Yeah\r\nIn-slum-national, underground\r\nThunder pounds when I stomp the ground (woo)\r\nLike a million elephants with silverback orangutans\r\nYou can't stop a train\r\nWho want some? Don't come un-prepared\r\nI'll be there, but when I leave there\r\nBetter be a household name\r\nWeather man tellin' us it ain't gon' rain\r\nSo now we sittin' in a drop-top, soakin' wet\r\nIn a silk suit, tryin' not to sweat\r\nHit somersaults without the net\r\nBut this'll be the year that we won't forget\r\nOne-nine-nine-nine, Anno Domini, anything goes, be whatchu wanna be\r\nLong as you know consequences are given for livin', the fence is\r\nToo high to jump in jail\r\nToo low to dig, I might just touch hell, hot\r\nGet a life, now they gon' sell\r\nThen I might catch you a spell, look at what came in the mail\r\nA scale and some Arm and Hammer, so grow grid and some baby mama\r\nBlack Cadillac and a pack of Pampers\r\nStack of question with no answers\r\nCure for cancer, cure for AIDS\r\nMake a nigga wanna stay on tour for days\r\nGet back home, things are wrong\r\nWhen I really knew it was bad all along\r\nBefore you left adds up to a ball of power\r\nThoughts at a thousands miles per hour\r\nHello, ghetto, let your brain breathe\r\nBelieve there's always mo', ow\r\n\r\nDon't pull the thang out, unless you plan to bang\r\nBombs over Baghdad\r\n(Yeah, ha ha yeah)\r\nDon't even bang unless you plan to hit something\r\nBombs over Baghdad, yeah\r\n(Yeah, uh-huh)\r\nDon't pull the thang out, unless you plan to bang\r\nBombs over Baghdad, yeah\r\n(Ha, ha, ha, yeah)\r\nDon't even bang unless you plan to hit something\r\nBombs over Baghdad, yeah\r\n\r\nUno, dos, tres, it's on\r\nDid you ever think a pimp rock a microphone?\r\nLike that there Boi and will still stay street\r\nBig things happen every time we meet\r\nLike a track team, crack fiend, dyin' to geek\r\nOutkast bumpin' up and down the street\r\nSlam back, Cadillac, 'bout five nigga deep\r\nSeventy-five emcee's freestylin' to the beat\r\n'Cause we get krunk, stay drunk, at the club\r\nShould have bought an ounce, but you caught the dub\r\nShould have held back, but you throwed the punch\r\n'Spose to meet your girl but you packed a lunch\r\nNo D to-the U to-the G for you\r\nGot a son on the way by the name of Bamboo\r\nGot a little baby girl four year, Jordan\r\nNever turn my back on my kids for them\r\nShould have hit it (hit it) quit it (quit it) rag (rag) top (top)\r\nBefore you read up, get a laptop\r\nMake a business for yourself, boy, set some goals\r\nMake a fair diamond out of dusty coals\r\nRecord number four, but we on a roll\r\nHold up, slow up, stop, control\r\nLike Janet, planets, Stankonia's on ya\r\nMovin like Floyd comin' straight to Florida\r\nLock all your windows then block the corridors\r\nPullin off a belt 'cause a whipping's in order\r\nLike a three-piece just 'fore I cut your daughter\r\nYo quiero Taco Bell, then I hit the border\r\nPenny pap rappers tryin' to get the five\r\nI'm a microphone fiend tryin' to stay alive\r\nWhen you come to ATL boi you betta not hide\r\n'Cause the Dungeon Family gon' ride, ha\r\n\r\nDon't pull the thang out, unless you plan to bang\r\nBombs over Baghdad\r\n(Ah, yeah)\r\nDon't even bang unless you plan to hit something\r\nBombs over Baghdad, yeah\r\n(Uh yeah)\r\nDon't pull the thang out, unless you plan to bang\r\nBombs over Baghdad, yeah\r\n(Y'all heard me, yeah)\r\nDon't even bang unless you plan to hit something\r\nBombs over Baghdad, yeah\r\n\r\nBombs over Baghdad, yeah\r\nBombs over Baghdad, yeah\r\nBombs over Baghdad, yeah\r\nBombs over Baghdad, yeah\r\n\r\n(B-I-G B-O-I)\r\n\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top\r\nBob your head, rag top (one, two, three, let's go)\r\n\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\n\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\n\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival\r\nPower music, electric revival",
        "lyrics_source": "Source: LyricFind",
    }
    embed_object = LyricsEmbed(**kwargs)

    assert check_description_requirements(embed=embed_object)
    assert check_field_requirements(embed=embed_object)


def check_field_requirements(embed: LyricsEmbed) -> bool:
    for field in embed.fields:
        assert len(field.value) <= 1024
    return True


def check_description_requirements(embed: LyricsEmbed) -> bool:
    return len(embed.description) <= 2048
