from django.core.urlresolvers import reverse
from django.test import TestCase
from musicapp.models import Album,Song,Artist
import musicapp.testutil as testutil
import musicapp.helpers as helper
class ViewTests(TestCase):
    '''
    Test case for Login page interface
    Login page should have: User Name, Password
    Login button

    '''
    def test_login_page_display_correctly(self):
        response = self.client.get(reverse('login'))
        # Check form is displayed correctly
        # user name control
        self.assertIn('class="form-control" type="text" name="username"', response.content.decode('utf-8'))
        # pass word control
        self.assertIn('class="form-control" type="password" name="password"', response.content.decode('utf-8'))
        # button control
        self.assertIn('button class="btn btn-primary btn-block" type="submit"', response.content.decode('utf-8'))

    '''
    Check home page display correctly
    '''
    def test_home_page_display_correctly(self):
        response = self.client.get(reverse('home'))

        # top songs tab
        self.assertIn('<a href="#top-songs" role="tab" data-toggle="tab">top songs</a>'.lower(), response.content.decode('utf-8').lower())

        # top albums tab
        self.assertIn('<a href="#top-albums" role="tab" data-toggle="tab">top albums</a>'.lower(),response.content.decode('utf-8').lower())

        #top artist tab
        self.assertIn('<a href="#top-artists" role="tab" data-toggle="tab">top artists</a>'.lower(),response.content.decode('utf-8').lower())


'''
Class for testing functionality
'''
class FunctionTest(TestCase):
    '''
    Test user profile, logout function is available only for authenticated user
    '''
    def test_login_required(self):
        testutil.create_user()
        self.client.login(username='testuser', password='test1234')
        response = self.client.get(reverse('home'))
        self.assertIn(reverse('logout'), response.content.decode('utf-8'))
        self.assertIn(reverse('profile'), response.content.decode('utf-8'))
    '''
    Test run query method
    1. Pass a parameter
    2. Check returned result if returned result is dictionary
    '''
    def test_run_query(self):
        returned_result = helper.run_query('Eminem','')
        self.assertIsInstance(returned_result,dict)
    '''
    Test detail artist method
    1.Login
    2. Create artist
    3. Call Artist view with parameter
    4. Check the specific album of this artist
    '''
    def test_detail_artist(self):
        testutil.create_user()
        self.client.login(username='testuser', password='test1234')
        testutil.create_artist()
        response = self.client.get(reverse('artist', args=['celine-dion']))
        # print(response.content)
        self.assertIn('/view/album/celine-dion/back-to-light-the-fm-radio-gods-remix-collection/'.lower(), response.content.decode('utf-8').lower())





