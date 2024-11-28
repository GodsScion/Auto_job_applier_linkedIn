

function clickFollowingButtons() {
    const buttons = Array.from(document.querySelectorAll('button'))
        .filter(button => button.textContent.trim() === 'Following' && button.checkVisibility());

    if (buttons.length) {
        buttons.forEach((button, i) => setTimeout(() => button.click(), i * 150));
        buttons[buttons.length - 1].scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(clickFollowingButtons, buttons.length * 150);
    }
};


function clickFollowingButtonsExpanded() {
    const allButtons = document.querySelectorAll('button');
    const buttons = Array.from(allButtons).filter(button => button.textContent.trim() === 'Following');

    if (buttons.length === 0) {
        return;
    }

    buttons.forEach((button) => {
        if (button.checkVisibility()) {
            setTimeout(() => {
                button.click();
            }, 150);
        }
    });
    
    buttons[buttons.length - 1].scrollIntoView({ behavior: 'smooth', block: 'center' });

    setTimeout(() => {
        clickFollowingButtons();
    }, 10000);
}





function clickFollowingButtons2() {
    const buttons = document.querySelectorAll('button');

    buttons.forEach((button) => {
        if (button.textContent.trim() === 'Following') {
            button.scrollIntoView({ behavior: 'smooth', block: 'center' });

            setTimeout(() => {
                button.click();
            }, 150);
        }
    });
}

function clickFollowingButtons3() {
    const buttons = document.evaluate("//button[normalize-space(text())='Following']", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
    let index = 0;

    const intervalId = setInterval(() => {
        if (index >= buttons.snapshotLength) {
            clearInterval(intervalId);
        } else {
            const button = buttons.snapshotItem(index);
            button.scrollIntoView({ behavior: 'smooth', block: 'center' });
            button.click();
            index++;
        }
    }, 150);
}



