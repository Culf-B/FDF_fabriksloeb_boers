import time
import pygame
import uielements

colors = {
    "Stålvarer": [100, 100, 255],
    "Brød": [255, 255, 100],
    "Tøj": [100, 255, 100],
    "Møbler": [200, 150, 100]
}

class Product:
    def __init__(self, basePrice, minPrice, maxPrice):
        self.timePassedSec = 0
        self.itemsSold = 1

        self.basePrice = basePrice
        self.minPrice = minPrice
        self.maxPrice = maxPrice

        self.prevDemand = 1

    def tick(self, deltaSec):
        self.timePassedSec += deltaSec

    def getSoldPrSec(self):
        if self.timePassedSec > 0:
            return self.itemsSold / self.timePassedSec
        else:
            return self.itemsSold

    def sell(self, amount = 1):
        self.itemsSold += amount

    def getPrice(self, demand):

        if demand > self.prevDemand + 0.1:
            demand = self.prevDemand + 0.1
        elif demand < self.prevDemand - 0.1:
            demand = self.prevDemand - 0.1
        self.prevDemand = demand

        self.currentPrice = self.basePrice * demand
        if self.currentPrice < self.minPrice: self.currentPrice = self.minPrice
        elif self.currentPrice > self.maxPrice: self.currentPrice = self.maxPrice

        return self.currentPrice
    
class Market:
    def __init__(self, productNames = ["Stålvarer", "Brød", "Tøj", "Møbler"]):
        self.timePassed = 0
        self.minute = -1
        
        self.products = {}
        self.prices = {}
        for productName in productNames:
            self.products[productName] = Product(10, 5, 20)
    
    def sell(self, productName, amount = 1):
        self.products[productName].sell(amount)
        return f'{amount} "{productName}" solgt til {round(self.prices[productName] * amount, 2)}kr ({round(self.prices[productName], 2)}kr pr. stk.)'

    def tick(self, deltaSec):
        # Update time
        self.timePassed += deltaSec

        for product in self.products.values():
            product.tick(deltaSec)

        # Market updates prices every minute (to prevent issues where first person who sells displaces market)
        if self.timePassed // 10 > self.minute:
            self.minute = self.timePassed // 10

            # Update prices
            self.totalSoldPrSec = 0
            for product in self.products.values():
                self.totalSoldPrSec += product.getSoldPrSec()

            for name, product in self.products.items():
                if product.getSoldPrSec() > 0:
                    tempDemand = (self.totalSoldPrSec / len(list(self.products))) / product.getSoldPrSec()
                else:
                    tempDemand = 1
                self.prices[name] = product.getPrice(tempDemand)

    def getPrices(self):
        return self.prices
    
    def getProducts(self):
        return self.products

class ProductGUI:
    def __init__(self, screen, rect, name, market, product, transactionHistoryBox):
        self.name = name
        self.screen = screen
        self.rect = rect
        self.font = pygame.font.SysFont("Consolas", 20)
        self.market = market
        self.product = product
        self.transactionHistoryBox = transactionHistoryBox

        self.window = uielements.Window(
            self.screen,
            self.rect, 
            [
                [0, 0, 0],
                [0, 0, 0],
                [255, 255, 255]
            ],
            borderwidth = 1
        )

        self.nameLabel = uielements.Text(
            self.window.getSurface(),
            pygame.Rect(0, 0, self.window.getWidth(), self.window.getHeight() // 7),
            {
                "standard": [
                    [0, 0, 0],
                    [0, 0, 0],
                    colors[self.name]
                ]
            },
            self.font,
            text = self.name,
        )

        self.sellAmountInput = uielements.Input(
            self.window.getSurface(),
            pygame.Rect(0, self.window.getHeight() // 7, self.window.getWidth() * 0.4, self.window.getHeight() // 7),
            {
                "standard": [
                    [0, 0, 0],  # Text color
                    [0, 0, 0],        # Border color
                    [200, 200, 200]   # Background color
                ],
                "hover": [
                    [0, 0, 0],  # Text color (white)
                    [100, 100, 100],     # Border color
                    [220, 220, 220]   # Background color
                ],
                "selected": [
                    [0, 0, 0],  # Text color
                    [100, 100, 255],  # Border color
                    [255, 255, 255]   # Background color
                ]
            },
            self.font,
            text = "1"
        )

        self.sellButton = uielements.Button(
            self.window.getSurface(),
            pygame.Rect(self.window.getWidth() * 0.4, self.window.getHeight() // 7, self.window.getWidth() * 0.6, self.window.getHeight() // 7),
            {
                "standard": [
                    [0, 0, 0],  # Text color
                    [0, 0, 0],        # Border color
                    [200, 200, 200]   # Background color
                ],
                "hover": [
                    [0, 0, 0],  # Text color (white)
                    [50, 50, 50],     # Border color
                    [150, 150, 150]   # Background color
                ],
                "click": [
                    [0, 0, 0],  # Text color
                    [100, 100, 100],  # Border color
                    [100, 100, 100]   # Background color
                ]
            },
            self.font,
            text = "Sælg!",
            command = self.sell
        )

        self.priceLabel = uielements.Text(
            self.window.getSurface(),
            pygame.Rect(0, 2 * self.window.getHeight() // 7, self.window.getWidth(), self.window.getHeight() // 7),
            {
                "standard": [
                    [0, 0, 0],
                    [0, 0, 0],
                    [255, 255, 255]
                ]
            },
            self.font,
            text = "Pris: ",
        )

        self.soldLabel = uielements.Text(
            self.window.getSurface(),
            pygame.Rect(0, 3 * self.window.getHeight() // 7, self.window.getWidth(), self.window.getHeight() // 7),
            {
                "standard": [
                    [0, 0, 0],
                    [0, 0, 0],
                    [255, 255, 255]
                ]
            },
            self.font,
            text = "Solgt: ",
        )

        self.doubleButton = uielements.Button(
            self.window.getSurface(),
            pygame.Rect(0.5 * self.window.getWidth(), 4 * self.window.getHeight() // 7, self.window.getWidth() * 0.5, self.window.getHeight() // 7),
            {
                "standard": [
                    [0, 0, 0],  # Text color
                    [0, 0, 0],        # Border color
                    [200, 200, 200]   # Background color
                ],
                "hover": [
                    [0, 0, 0],  # Text color (white)
                    [50, 50, 50],     # Border color
                    [150, 150, 150]   # Background color
                ],
                "click": [
                    [0, 0, 0],  # Text color
                    [100, 100, 100],  # Border color
                    [100, 100, 100]   # Background color
                ]
            },
            self.font,
            text = "2x",
            command = self.priceDouble
        )

        self.halfButton = uielements.Button(
            self.window.getSurface(),
            pygame.Rect(0, 4 * self.window.getHeight() // 7, self.window.getWidth() * 0.5, self.window.getHeight() // 7),
            {
                "standard": [
                    [0, 0, 0],  # Text color
                    [0, 0, 0],        # Border color
                    [200, 200, 200]   # Background color
                ],
                "hover": [
                    [0, 0, 0],  # Text color (white)
                    [50, 50, 50],     # Border color
                    [150, 150, 150]   # Background color
                ],
                "click": [
                    [0, 0, 0],  # Text color
                    [100, 100, 100],  # Border color
                    [100, 100, 100]   # Background color
                ]
            },
            self.font,
            text = "0.5x",
            command = self.priceHalf
        )

        self.priceIndexLabel = uielements.Text(
            self.window.getSurface(),
            pygame.Rect(0, 5 * self.window.getHeight() // 7, self.window.getWidth(), self.window.getHeight() // 7),
            {
                "standard": [
                    [0, 0, 0],
                    [0, 0, 0],
                    [255, 255, 255]
                ]
            },
            pygame.font.SysFont("consolas", 15),
            text = "0, 0, 0"
        )

        self.window.add_elements(
            self.nameLabel,
            self.sellAmountInput,
            self.sellButton,
            self.priceLabel,
            self.soldLabel,
            self.doubleButton,
            self.halfButton,
            self.priceIndexLabel
        )

    def priceDouble(self):
        self.market.products[self.name].basePrice *= 2
        self.market.products[self.name].minPrice *= 2
        self.market.products[self.name].maxPrice *= 2

    def priceHalf(self):
        self.market.products[self.name].basePrice *= 0.5
        self.market.products[self.name].minPrice *= 0.5
        self.market.products[self.name].maxPrice *= 0.5

    def sell(self):
        try:
            self.transactionHistoryBox.text.append(
                self.market.sell(self.name, int(self.sellAmountInput.getText()))
            )
        except Exception as e:
            print(f'Error when trying to sell: {e}')
            self.sellAmountInput.text = "1"

    def update(self, events, deltaInSec, price, totalSold):
        self.priceLabel.text = f'Pris: {round(price, 2)}'
        self.soldLabel.text = f'Solgt: {totalSold}'
        self.priceIndexLabel.text = f'mn{self.market.products[self.name].minPrice},b{self.market.products[self.name].basePrice},mx{self.market.products[self.name].maxPrice}'
        self.window.update(events, 1, deltaInSec)

# Generel control vars
run = True

# Market setup
market = Market()

# GUI setup
pygame.init()
screen = pygame.display.set_mode([900, 450], pygame.FULLSCREEN)
pygame.display.set_caption("Børsen")
clock = pygame.time.Clock()



productGuis = {}

products = market.getProducts()

transactionHistoryBox = uielements.Scrolledtext(
    screen,
    pygame.Rect(0, screen.get_height() // 2, screen.get_width(), screen.get_height() // 2),
    uielements.defaultScrolledTextColorScheme,
    pygame.font.SysFont("consolas", 20),
    allign = "LEFT"
)

productSurface = pygame.Surface([screen.get_width() * (len(list(products)) / (len(list(products)))), screen.get_height() // 2])
print(productSurface.get_width())
for i in range(len(list(products.keys()))):
    productGuis[list(products.keys())[i]] = ProductGUI(
        productSurface,
        pygame.Rect(
            (productSurface.get_width() // len(list(products))) * i,
            0,
            productSurface.get_width() // len(list(products)),
            productSurface.get_height()
        ),
        list(products.keys())[i],
        market,
        products[list(products.keys())[i]],
        transactionHistoryBox
    )



# Time setup
prevTime = time.time()

# Main loop
while run:
    # Events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            run = False

    # Market timing
    deltaSec = time.time() - prevTime
    prevTime = time.time()

    # Market update
    market.tick(deltaSec)
    print(market.getPrices(), market.timePassed, market.minute)

    # Clear GUI
    screen.fill([255, 255, 255])

    # Draw GUI
    for name, productGUI in productGuis.items():
        productGUI.update(events, deltaSec, market.getPrices()[name], market.products[name].itemsSold - 1)
        
    transactionHistoryBox.update(events, deltaInSec = deltaSec)

    screen.blit(productSurface, [0, 0])

    # GUI window update
    pygame.display.update()
    clock.tick(60)