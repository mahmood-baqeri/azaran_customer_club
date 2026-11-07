// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################            Domain
let windowLocation = window.location.href;
let Domain = windowLocation.includes("hrclub") ? "https://hrclub.azaran.group/manager/" : "http://127.0.0.1:8080/";

// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################            AJAX
const ajaxFunction = (url, param = null, convertToStringify = true) => {
    return new Promise((resolve) => {
        $.ajax({
            method: "post",
            url: url.includes("http") ? url : Domain + url,
            dataType: "json",
            headers: {'X-CSRFToken': functionGetMyCookies('csrftoken')},
            data: convertToStringify ? JSON.stringify({param}) : param, // data: JSON.stringify({param}),
            beforeSend: function () {
                console.log('####################  send')
            },
            success: function (response, status, $this) {
                console.log('####################  response')
                if ($this.status == 200) resolve(JSON.parse(response.data)); else if ($this.status == 201) resolve(response); else {
                    resolve([response, $this.status]);
                }
                /*
                      200   respnse serialaize     array
                      201   respnse sample         array
                      202   respnse text           success
                      203   respnse text           error
                 */
            },
            done: function (result) {
                console.log('####################  result')
            },
            error: function (error) {
                // debugger;
                console.log('####################  error')
                //console.log(error);
            }
        });
    });
};

const ajaxForm = (url, formData) => {
    return new Promise((resolve) => {
        $.ajax({
            url: url, type: 'POST', data: formData, success: function (response, status, $this) {
                resolve([$this.status == 200 ? JSON.parse(response.data) : response.data, $this.status]);
            }, error: function (response) {
                console.log('####################  error  ' + response)
            }, cache: false, contentType: false, processData: false
        });
    });
};


// ######################   CSRF
const functionGetMyCookies = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################            Cookie
function setCookieMe(cookieName, cookieValue, expireDay = 5) {
    const d = new Date();
    d.setTime(d.getTime() + (expireDay * 24 * 60 * 60 * 1000));
    let expires = "expires=" + d.toUTCString();
    document.cookie = cookieName + "=" + cookieValue + ";" + expires + ";path=/";
}

function getCookieMe(cookieName) {
    let name = cookieName + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################            Convert Date
function gregorianToJalali(inputDate) {
    // "2022-08-14T05:03:48.048Z"
    split = inputDate.split("T");
    day = split[0].split("-");
    time = split[1].split(":");
    const date = new Date(Date.UTC(day[0], day[1], day[2], time[0], time[1], 0, 0));

    const faDate = new Intl.DateTimeFormat("fa", {
        // weekday: "long",
        year: "numeric", month: "long", day: "numeric"
    }).format(date);

    return faDate
}


// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################            menu active Item
$(document).ready(function () {
    $('.bottomMenuSection a.nav-link').on('click', function () {
        setCookieMe('menuActiveNav', $(this).attr('data-active'), 2)
    });
    let activeTab = getCookieMe('menuActiveNav');
    if (activeTab)
        $('.bottomMenuSection a[data-active=' + activeTab + ']').addClass('active');
});


// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################            header Menu location
$(document).ready(function () {
    let location = window.location.pathname;
    $('.sideNavLinks li').each(function (index, element) {
        if ($(element).find('a').attr('href') === location) {
            $(element).addClass('active');
        }
    });


    //  activate current menu in side bar
    let headerLocation = window.location;
    $('#main-menu-navigation a').each(function () {
        if (($(this).attr('href') + '/') == headerLocation || $(this).attr('href') == headerLocation) {

            $(this).parents('.menu-content').parent().addClass('menu-collapsed-open', 'open');
            $(this).parent().addClass('active');
        }
    });
});

// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################            delete modal
//  Delete modal
$(document).on('click', '.btnDeleteWithModal', function () {
    let modal = $('#deleteModal');
    let data = $(this).data();
    modal.find('form').attr('action', data.action);
});

// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################             user Favorites
$(document).on('click', '.likeAndDislikeProductEl', function () {
    let inputs = {
        'id': $(this).attr('data-productId'),
    };
    ajaxFunction("user/api/like", inputs, true).then((data) => {
        if (data[0].data == 'added')
            $(this).addClass('liked');
        else {
            $(this).parents('.wishlist-item').remove();
            $(this).removeClass('liked')
        }

        $('#cart-target .number').text(data[0].count)
        let products = data[0].products;
        handelUserFavorites(products);
    });
});

function allUserFavorites() {
    ajaxFunction("user/api/like/all", [], true).then((data) => {
        let products = data[0].data;
        $('#cart-target .number').text(data[0].count)
        handelUserFavorites(products);
    });
}

function handelUserFavorites(products) {
    $('#headerUserFavorites > .row').remove();
    $.each(products, function (key, item) {
        let newItem = $('.headerFavoriteAppendItem').clone();
        newItem.find('.likeAndDislikeProductEl').attr('data-productId', item.id);
        newItem.removeClass('d-none headerFavoriteAppendItem');
        let href = newItem.find('.cart-image').attr('href');
        href = href + '?slug=' + item.slug;
        newItem.find('.cart-image').attr('href', href)
        newItem.find('.title').attr('href', href).text(item.title)
        let src = newItem.find('.photo').attr('src');
        src = src + item.file;
        newItem.find('.photo').attr('src', src);
        newItem.find('.money').text(item.price + " تومان");
        $('#headerUserFavorites').append(newItem);
    });
}

// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################            sweet alert
jQuery(document).ready(function ($) {
    $("#adminPanelLoader").addClass('display-none');
    $(document).on('click', '.deleteRecordFromTable', function (event) {
        event.preventDefault();
        let id = $(this).attr('data-deleteId');
        swal({
            title: "آیا مطمئن هستید؟",
            text: "بعد از حذف دیگر قابلیت بازگردانی وجود ندارد.",
            type: "warning",
            showCancelButton: true,
            confirmButtonText: 'بله حذف شود',
            cancelButtonText: 'نه لغو شود',
            closeOnConfirm: false
        }, function () {
            document.getElementById("deleteRecordForm_" + id).submit();
        });
    });
});

// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################            Posts
$(document).ready(function () {
    const postLoader = $('.postCommentsSection .loaderSection');

    function handelCommentLocation() {
        let ulElement = $('.postCommentsSection ul');
        ulElement.animate({scrollTop: ulElement.prop("scrollHeight") + 1000}, 1500);
    }


    $('#postCommentFormElement').on('submit', function (e) {
        e.preventDefault()
        postLoader.toggleClass('d-none');
        let element = $(this);
        ajaxForm($(this).attr('action'), new FormData(this)).then((data) => {
            if (data[1] == 203) MyNotification('خطا !', data[0][0], 'error')

            if (data[1] == 201) {
                element.find('textarea').val('');
                let item = element.parent().parent().find('.commentNewMsgItem').clone();
                item.removeClass('commentNewMsgItem d-none');
                item.attr('id', `chatElementId___${data[0][1][0]['id']}`);
                item.find('.user img').attr('src', data[0][1][0]['userPhoto']);
                item.find('.user span').text(data[0][1][0]['date']);

                // if (data[0][1][0]['forMe'])
                //     item.find('.user .deleteElement').removeClass('d-none').attr('data-id', data[0][1][0]['id']);

                item.find('.content p').text(data[0][1][0]['text']);
                element.parent().parent().find('ul').append(item);
            }
            postLoader.toggleClass('d-none');
            handelCommentLocation();
        });
    })


    $('body').on('click', '.___postSection .heart', function () {
        element = $(this);
        let inputs = {
            'id': $(this).attr('data-id'),
        };
        ajaxFunction("api/post/like", inputs, true).then((data) => {
            let likeCountElement = element.find('span');
            let likeCount = parseInt(likeCountElement.text());
            if (data.data == 'added') {
                element.addClass('liked');
                likeCountElement.text(likeCount > 1 ? likeCount + 1 : 1)
            } else {
                element.removeClass('liked');
                likeCountElement.text(likeCount > 0 ? likeCount - 1 : 0)
            }
        });
    })

})


// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################       Charity
$('.charitySendScoreModalBtn').on('click', function () {
    let modal = $('#charitySendScoreModal');
    modal.find('input[name=charity_id]').val($(this).attr('data-id'));
});
$('#charitySendScoreModal input[name=point]').on('keyup change', function () {
    if (parseInt($(this).val()) > parseInt($(this).attr('data-max'))) {
        $(this).next().removeClass('d-none');
    } else {
        $(this).next().addClass('d-none');
    }
});

// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################       Partner
$('.partnerSendScoreModalBtn').on('click', function () {
    let modal = $('#partnerSendScoreModal');
    modal.find('input[name=charity_id]').val($(this).attr('data-id'));
});
$('#partnerSendScoreModal input[name=point]').on('keyup change', function () {
    if (parseInt($(this).val()) > parseInt($(this).attr('data-max'))) {
        $(this).next().removeClass('d-none');
    } else {
        $(this).next().addClass('d-none');
    }
});

// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################       Score
$('#sendScoreModal input[name=point]').on('keyup change', function () {
    if (parseInt($(this).val()) > parseInt($(this).attr('data-max'))) {
        $(this).next().removeClass('d-none');
    } else {
        $(this).next().addClass('d-none');
    }
});
$('#cashScoreModal input[name=point]').on('keyup change', function () {
    if (parseInt($(this).val()) > parseInt($(this).attr('data-max'))) {
        $(this).next().removeClass('d-none');
    } else {
        $(this).next().addClass('d-none');
    }
});


$('.bookDownloadBtn').on('click', function () {
    ajaxFunction("api/bookDownload", {'book_id': $(this).attr('data-id')}, true).then((data) => {
    });
});


// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################       handel Modals
$('.uploadDataWithExcel').on('click', function () {
    let modal = $('#uploadDataWithExcel');
    modal.find('form').attr('action', $(this).attr('data-action'))
    modal.find('.m-title').text($(this).attr('data-title'))

    if ($(this).attr('data-help')) {
        modal.find('.help').removeClass('d-none');
        modal.find('.help').find('a').attr('href', $(this).attr('data-help'));
    } else
        modal.find('.help').addClass('d-none');

    modal.modal('show');
});

$('.forgetPassModalBtn').on('click', function () {
    $('#loginModal').modal('hide');
    $('#forgetPassModal').modal('show');
});

$('.loginModalBtn').on('click', function () {
    $('#registerModal').modal('hide');
    $('#loginModal').modal('show');
});

$('.registerModalBtn').on('click', function () {
    $('#loginModal').modal('hide');
    $('#registerModal').modal('show');
});

$('.btnRemoveItem').on('click', function () {
    let modal = $('#deleteModal');
    modal.modal('show');
    modal.find('.title').text($(this).attr('data-title'));
    modal.find('form').attr('action', $(this).attr('data-url'));
});
$('.reserveBookModalBtn').on('click', function () {
    let modal = $('#reserveBookModal');
    modal.find('input[name=charity_id]').val($(this).attr('data-id'));
});

$(document).ready(function () {
    $('.btnLoginModal').on('click', function () {
        $('.sidebar.show').removeClass('show');
        $('.menu-toggler.show').removeClass('show');
    })
});


// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################      Assessment
$('.assessmentElement').on('click', function () {
    $.post("https://assessment.azaran-group.com/admin/ApiUser/loginUser_nsdmclkmslcmsljmls5sx5s5xvgdsvm54s5f5csf", {'nationalCode': $(this).attr('data-nationalCode')}, function (result) {
        res = JSON.parse(result);
        // window.location.href = 'https://assessment.azaran-group.com/dashboard/?userToken=' + res.data.token + '&userId=' + res.data.id;

        window.open(
            'https://assessment.azaran-group.com/dashboard/?userToken=' + res.data.token + '&userId=' + res.data.id,
            '_blank'
        );
    });
});


// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################      Other
$('.linkElement').each(function (index, element) {
    $(element).attr('href', Domain + $(element).attr('data-link'))
});


// ##################################################################
// ##################################################################
// ##################################################################
// ##################################################################      Export In Excel
function functionExcelReport() {
    let table1 = document.getElementById('theMainTabelElement');
    if (table1) {
        let wb1 = XLSX.utils.table_to_book(table1, { sheet: "Sheet1" });
        XLSX.writeFile(wb1, 'report.xlsx');
    }

    let table2 = document.getElementById('theMainTabelElement__2');
    if (table2) {
        let wb2 = XLSX.utils.table_to_book(table2, { sheet: "Sheet1" });
        XLSX.writeFile(wb2, 'report_2.xlsx');
    }
}
