from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.utils import timezone
from decimal import Decimal
import random
from apps.receipts.models import Receipt
from apps.restaurants.models import Restaurant
from faker import Faker



User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Create fake data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of users to create'
        )
        parser.add_argument(
            '--restaurants',
            type=int,
            default=50,
            help='Number of restaurants to create'
        )
        parser.add_argument(
            '--receipts',
            type=int,
            default=200,
            help='Number of receipts to create'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting to create fake data...')
        )

        # Create users
        users_count = options['users']
        self.create_users(users_count)

        # Create restaurants
        restaurants_count = options['restaurants']
        self.create_restaurants(restaurants_count)

        # Create receipts
        receipts_count = options['receipts']
        self.create_receipts(receipts_count)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {users_count} users, '
                f'{restaurants_count} restaurants, and {receipts_count} receipts'
            )
        )

    def create_users(self, count):
        """Create fake users"""
        self.stdout.write(f'Creating {count} users...')
        
        # Define user roles - adjust these based on your UserRoles choices
        roles = ['GUEST', 'USER', 'ADMIN']  # Modify based on your UserRoles enum
        
        users = []
        for i in range(count):
            email = fake.unique.email()
            user = User(
                email=email,
                username=email,  # If your User model still uses username
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=random.choice(roles),
                is_active=True,
                date_joined=fake.date_time_between(
                    start_date='-2y', 
                    end_date='now', 
                    tzinfo=timezone.get_current_timezone()
                )
            )
            user.set_password('password123')  # Set a default password
            users.append(user)
        
        User.objects.bulk_create(users, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(f'Created {count} users')
        )

    def create_restaurants(self, count):
        """Create fake restaurants"""
        self.stdout.write(f'Creating {count} restaurants...')
        
        # Common cuisine types
        cuisine_types_options = [
            ['Italian'], ['Chinese'], ['Mexican'], ['American'], ['Indian'],
            ['Thai'], ['Japanese'], ['French'], ['Greek'], ['Mediterranean'],
            ['Italian', 'Pizza'], ['Asian', 'Chinese'], ['Mexican', 'Tex-Mex'],
            ['American', 'Burgers'], ['Indian', 'Vegetarian'],
            ['Thai', 'Asian'], ['Japanese', 'Sushi'], ['French', 'European'],
            ['Greek', 'Mediterranean'], ['Fast Food', 'American']
        ]
        
        # Sample hours format
        def generate_hours():
            return {
                'monday': {'open': '09:00', 'close': '22:00'},
                'tuesday': {'open': '09:00', 'close': '22:00'},
                'wednesday': {'open': '09:00', 'close': '22:00'},
                'thursday': {'open': '09:00', 'close': '22:00'},
                'friday': {'open': '09:00', 'close': '23:00'},
                'saturday': {'open': '10:00', 'close': '23:00'},
                'sunday': {'open': '10:00', 'close': '21:00'},
            }
        
        restaurants = []
        for i in range(count):
            # Generate coordinates around a central point (adjust as needed)
            # These coordinates are roughly around New York City
            lat = fake.latitude()
            lon = fake.longitude()
            
            restaurant = Restaurant(
                place_id=f"place_{fake.uuid4()}",
                name=fake.company() + " " + random.choice([
                    'Restaurant', 'Bistro', 'Cafe', 'Grill', 'Kitchen',
                    'Eatery', 'Diner', 'Bar & Grill'
                ]),
                address=fake.address(),
                cuisine_types=random.choice(cuisine_types_options),
                rating=round(random.uniform(2.0, 5.0), 1),
                price_level=random.randint(1, 4),
                location=Point(float(lon), float(lat)),
                website=fake.url() if random.choice([True, False]) else None,
                phone_number=fake.phone_number()[:20] if random.choice([True, False]) else None,
                hours=generate_hours() if random.choice([True, False]) else None,
                created_at=fake.date_time_between(
                    start_date='-1y', 
                    end_date='now',
                    tzinfo=timezone.get_current_timezone()
                ),
                updated_at=timezone.now()
            )
            restaurants.append(restaurant)
        
        Restaurant.objects.bulk_create(restaurants, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(f'Created {count} restaurants')
        )

    def create_receipts(self, receipts_count):
        """Create fake receipts"""
        self.stdout.write(f'Creating {receipts_count} receipts...')
        
        # Get all users and restaurants
        users = list(User.objects.all())
        restaurants = list(Restaurant.objects.all())
        
        if not users:
            self.stdout.write(
                self.style.ERROR('No users found. Create users first.')
            )
            return
            
        if not restaurants:
            self.stdout.write(
                self.style.ERROR('No restaurants found. Create restaurants first.')
            )
            return
        
        receipts = []
        for i in range(receipts_count):
            # Random date within the last year
            receipt_date = fake.date_between(start_date='-1y', end_date='today')
            
            receipt = Receipt(
                user=random.choice(users),
                restaurant=random.choice(restaurants),
                date=receipt_date,
                price=Decimal(str(round(random.uniform(5.0, 150.0), 2))),
                address=fake.address(),
                is_processed=random.choice([True, False]),
                image_url=fake.image_url() if random.choice([True, False]) else None,
                created_at=fake.date_time_between(
                    start_date=receipt_date,
                    end_date='now',
                    tzinfo=timezone.get_current_timezone()
                ),
                updated_at=timezone.now()
            )
            receipts.append(receipt)
        
        Receipt.objects.bulk_create(receipts, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(f'Created {receipts_count} receipts')
        )