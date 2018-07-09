from django.conf.urls import url

from views import (
    GetImageFile,
    JudgeImageFileExist,
    UpdateImageFile,
    DeleteImageFile,
    CreateImageFile,
    ImageCreatePage,
    ImageEditPage,
    ImageListPage,
    ListImage,
    DeleteOneImage
)

urlpatterns = [
    url(r'^GetImageFile$', GetImageFile.as_view()),
    url(r'^JudgeImageFileExist$', JudgeImageFileExist.as_view()),
    url(r'^CreateImageFile$', CreateImageFile.as_view()),
    url(r'^UpdateImageFile$', UpdateImageFile.as_view()),
    url(r'^DeleteImageFile$', DeleteImageFile.as_view()),

    url(r'^customize/create_image$', ImageCreatePage.as_view()),
    url(r'^customize/edit_image$', ImageEditPage.as_view()),
    url(r'^customize/images$', ImageListPage.as_view()),

    url(r'^describe_images$', ListImage.as_view()),
    url(r'^delete_image$', DeleteOneImage.as_view()),
]
