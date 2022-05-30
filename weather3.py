import requests
from flask import Flask , render_template,redirect, url_for,request, flash
from flask_sqlalchemy import SQLAlchemy

API_KEY = "65c3040ea79ee8e053a60ed4a1124a7c"
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret'



db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name= db.Column(db.String(50), nullable = False)
    Country = db.Column(db.String(100), nullable = True)


def GetWeather(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
    res = requests.get(url).json()

    return res
@app.route('/',methods = ['GET'])
def get_index():
    cities = City.query.all()
    
    weather_list = []    
    for city in cities:
        res = GetWeather(city.name)
        if res['cod'] =='404':
            print('ERROR CITY NOT FOUND')
        weather = {
                    'city':city.name,
                    'temperture':round((int(res['main']['temp']) -273.15) * 9/5 + 32 ,1),
                    'description':res['weather'][0]['description'],
                    'icon':res['weather'][0]['icon'],
                    'country':res['sys']['country']
                }
        weather_list.append(weather)

    return render_template('weather.html', weather_list = weather_list)




@app.route('/',methods = ['POST'])
def post_index():
    new_city = request.form.get('city')
    error_msg = ''
    _country = ''
    if new_city:
        existing_city = City.query.filter_by(name = new_city).first()
        if not existing_city:
            res = GetWeather(new_city)
            if res['cod'] ==200:
                new_city_ob = City(name = res['name'], Country = res['sys']['country'])
                db.session.add(new_city_ob)
                db.session.commit()
                _country = res['sys']['country']
            else:
                error_msg+='City Doesn\'t Exist'
        else:
            error_msg+='City Already Exists in the Database'
    if not new_city:
        error_msg = 'Nothing to add!'
    if error_msg:
        flash(error_msg,'Error')
    else:
        flash(f'City {new_city}, {_country} Added')

    return redirect(url_for('get_index'))


@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name = name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'Successfully deleted {city.name}, {city.Country} !', 'sucess')
    return redirect(url_for('get_index'))

if __name__ == "__main__":
	app.run(host='0.0.0.0', port='5000',debug = True)



# {
#     'coord': {'lon': -76.6122, 'lat': 39.2904},
#     'weather': [{'id': 802, 'main': 'Clouds', 'description': 'scattered clouds', 'icon': '03d'}],
#     'base': 'stations', 
#     'main': {'temp': 305.02, 'feels_like': 309.34, 'temp_min': 301.47, 'temp_max': 307.69, 'pressure': 1014, 'humidity': 58},
#     'visibility': 10000,
#     'wind': {'speed': 3.6, 'deg': 260},
#     'clouds': {'all': 40},
#     'dt': 1653244207,
#     'sys': {'type': 2, 'id': 2046179, 'country': 'US', 'sunrise': 1653212851, 'sunset': 1653265141},
#     'timezone': -14400,
#     'id': 4347778,
#     'name': 'Baltimore',
#     'cod': 200
# }