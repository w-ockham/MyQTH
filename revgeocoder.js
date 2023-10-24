const endpoint = {
    'revgeocode':'https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress',
    'elevation':'https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php',
    'muni' : 'https://www.sotalive.net/api/reverse-geocoder/LonLatMuniToAddress',
};

const cache_rev = new Map();

async function local_reverse_geocoder(lat, lng, elev) {
    let pos = '?lat=' + String(lat) + '&lon=' + String(lng);

    if (cache_rev.has(pos)) {
	return cache_rev.get(pos);
    }

    if (cache_rev.size >= 16) {
	const oldest = cache_rev.keys().next().value;
	cache_rev.delete(oldest);
    }
    
    let rev_uri = endpoint['revgeocode'] + pos
    let elev_uri = endpoint['elevation'] + pos + '&outtype=JSON'
    let res_elev = null;

    if (elev) 
	res_elev = local_get_elevation(lat, lng);

    let res = await fetch(rev_uri);
    res = await res.json();

    if (!('results' in res)) {
	const p_err = Promise.resolve({'errors': 'OUTSIDE_JA'});
	cache_rev.set(pos, p_err);
	return p_err;
    }
    
    let muni_uri =
	endpoint['muni'] + pos + '&muni=' + res['results']['muniCd'];
    let res2 = await fetch(muni_uri);
    let result = await res2.json()
    result['addr1'] = res['results']['lv01Nm']
    result['errors'] = 'OK'
    
    if (elev) {
	const p_elev =  res_elev
	      .then(res => {
		  result['elevation'] = res['elevation']
		  result['hsrc'] = res['hsrc']
		  if (res['elevation'] == '-----')
		      result['errors'] = 'OUTSIDE_JA';
		  return Promise.resolve(result);});
	cache_rev.set(pos, p_elev);
	return p_elev;
    } else {
	const p_pos = Promise.resolve(result);
	cache_rev.set(pos, p_pos);
	return p_pos;
    }
}

const cache_elev = new Map();

async function local_get_elevation(lat, lng) {
    let pos = '?lat=' + String(lat) + '&lon=' + String(lng);
    let result = {};
    
    if (cache_elev.has(pos)) {
	return cache_elev.get(pos);
    }

    if (cache_elev.size >= 16) {
	const oldest = cache_elev.keys().next().value;
	cache_elev.delete(oldest);
    }
    
    let elev_uri = endpoint['elevation'] + pos + '&outtype=JSON';
    let res_elev = fetch(elev_uri)
	.then(res => res.json())
	.then(res => {
	    result['elevation'] = res['elevation']
	    result['hsrc'] = res['hsrc']
	    if (res['elevation'] == '-----')
		result['errors'] = 'OUTSIDE_JA';
	    else
		result['errors'] = 'OK';
	    return result;
	});
    
    cache_elev.set(pos,res_elev);
    
    return res_elev;
}

