from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import time
import random
# Create your views here.

#List of Quotes
quotes = ["Writing is easy. All of you have to do is cross out the wrong words.", "Everything has its limit - iron ore cannot be educated into gold.", 
          "I’ve lived through some terrible things in my life, some of which actually happened.", "I don’t like to commit myself about Heaven and Hell, you see, I have friends in both places.",
          "If you don’t read the newspaper, you’re uninformed. If you read the newspaper, you’re mis-informed.", "Be good and you will be lonesome.",
          "Clothes do not merely make a man...clothes are the man.", "A full belly is little worth when the mind is starved.", "Nothing needs so reforming as other people's habits.",
          "Architects cannot teach nature anything.", "There is no sadder than a young pessimist...except an old optimist.",
          "A man cannot be comofortable without his own approval.", "Travel is a fatal prejudice.", "Thunder is good, thunder is impressive; but it is lightning that does the work.",
          "Everyday throughout America, the Overspeeder runs over somebody and 'escapes.' That is the way it reads. At present the 'mobile numbers are so small that ordinary eyes cannot read them, upon a swiftly receding machine, at a distance of a hundred feet--a distance which the machine has covered before the spectator can adjust his focus. I think I would amend the law. I would enlarge the numbers, and make them readable at a hundred yards. For overspeeding--first offence--I would enlarge the figures again, and make them readable at three hundred yards--this in place of a fine, and as a warning to pedestrians to climb a tree.",
          "It is my belief that nearly any invented quotation, played with confidence, stands a good chance to deceive.", "The report of my death was an exaggeration. (Note to a London reporter, May 1897)"]


#List of Images
images = ["https://cdn.britannica.com/83/136283-050-9C9D6ED8/Mark-Twain-1907.jpg", "https://www.themorgan.org/sites/default/files/images/exhibitions/twain_ma7253_PainePhoto_No4.jpg", 
          "https://assets.editorial.aetnd.com/uploads/2010/04/mark-twain-gettyimages-683484482.jpg", "https://th-thumbnailer.cdn-si-edu.com/Bysr6nOR-Y0eX6S4H2h6OURXTIQ=/1000x750/filters:no_upscale()/https://tf-cmsv2-smithsonianmag-media.s3.amazonaws.com/filer/f6/88/f688e680-3907-409f-890e-1f21c8d0c8fe/10498071004_e99fe14563_o.jpg",
          "https://cdn.britannica.com/57/96657-050-087406C4/Mark-Twain-1907.jpg", "https://media.newyorker.com/photos/59ee271c4d2a207182a81b01/master/pass/Piepenbring-Mark-Twain.jpg", "https://marktwainhouse.org/wp-content/uploads/2021/07/IMG_1998-scaled.jpg"]

def main_page(request):
    quote = random.choice(quotes)
    image = random.choice(images)

    context = {
        'quote': quote,
        'image': image
    }
    return render(request, 'quotes/quote.html', context)

def show_all(request):
    context = {
        'quotes': quotes,
        'images': images
    }
    return render(request, 'quotes/show_all.html', context)

def about_page(request):
    context = {
        'person_name': "Mark Twain",
        'biography': "Samuel Langhorne Clemens, known by the pen name Mark Twain, was an American writer, humorist, and essayist. He was praised as the 'greatest humorist the United States has produced,' with William Faulkner calling him 'the father of American literature.'",
        'creator_note': "This web application was created by Nathaniel Clizbe."
    }
    return render(request, 'quotes/about.html', context)