import os
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.decorators.http import require_POST
from http import upload_receive, UploadResponse, JFUResponse

from clients.models import ProfileImage, ClientProfile

@require_POST
def upload(request):

    # The assumption here is that jQuery File Upload
    # has been configured to send files one at a time.
    # If multiple files can be uploaded simulatenously,
    # 'file' may be a list of files.

    profile_id = request.POST.get('profile_id', None)
    profile = None
    try:
        profile = ClientProfile.objects.get(id = profile_id)
    except:
        pass
    file = upload_receive(request)

    #TODO: check if each file is also deleted from disk
    for image in ProfileImage.objects.filter(profile = profile):
        image.delete()
    
    instance = ProfileImage(image = file, profile = profile)
    instance.save()

    basename = os.path.basename(instance.image.path)

    file_url = instance.image.url

    file_dict = {
        'name' : basename,
        'size' : file.size,

        'url': file_url,
        'thumbnailUrl': file_url,

        #'deleteUrl': reverse('jfu_delete', kwkrgs = { 'pk': instance.pk }),
        #'deleteType': 'POST',
    }

    return UploadResponse( request, file_dict )
